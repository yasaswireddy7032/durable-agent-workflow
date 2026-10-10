import sqlite3,json,hashlib
class Workflow:
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,payload TEXT,state TEXT,result TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,job TEXT,event TEXT);
        """)
    def submit(self,key,payload):
        encoded=json.dumps(payload,sort_keys=True)
        with self.db:
            old=self.db.execute('SELECT payload FROM jobs WHERE id=?',(key,)).fetchone()
            if old and old[0]!=encoded: raise ValueError('Idempotency key reused for different request')
            if not old:
                self.db.execute('INSERT INTO jobs VALUES(?,?,?,NULL)',(key,encoded,'awaiting_approval'))
                self.db.execute('INSERT INTO events(job,event) VALUES(?,?)',(key,'submitted'))
        return self.get(key)
    def get(self,key):
        row=self.db.execute('SELECT state,result FROM jobs WHERE id=?',(key,)).fetchone()
        if row is None: raise KeyError(key)
        return {'state':row[0],'result':json.loads(row[1]) if row[1] else None}
    def approve(self,key):
        with self.db:
            n=self.db.execute("UPDATE jobs SET state='approved' WHERE id=? AND state='awaiting_approval'",(key,)).rowcount
            if n:self.db.execute('INSERT INTO events(job,event) VALUES(?,?)',(key,'approved'))
        return self.get(key)
    def run(self,key):
        # A local deterministic tool executes inside one transaction. Remote side effects
        # would require an outbox and idempotency at the remote endpoint.
        try:
            self.db.execute('BEGIN IMMEDIATE')
            state=self.get(key)
            if state['state']=='completed': self.db.commit();return state
            if state['state']!='approved': raise PermissionError('Explicit approval required')
            payload=json.loads(self.db.execute('SELECT payload FROM jobs WHERE id=?',(key,)).fetchone()[0])
            items=payload.get('items',[])
            if not isinstance(items,list) or any(not isinstance(v,str) for v in items): raise ValueError('items must be strings')
            result={'count':len(items),'digest':hashlib.sha256('\n'.join(sorted(items)).encode()).hexdigest()}
            self.db.execute("UPDATE jobs SET state='completed',result=? WHERE id=?",(json.dumps(result),key))
            self.db.execute('INSERT INTO events(job,event) VALUES(?,?)',(key,'completed'))
            self.db.commit()
            return self.get(key)
        except Exception:
            self.db.rollback();raise
    def audit(self,key): return [r[0] for r in self.db.execute('SELECT event FROM events WHERE job=? ORDER BY seq',(key,))]
if __name__=='__main__':
    w=Workflow();w.submit('demo',{'items':['invoice','receipt']});w.approve('demo')
    print(json.dumps({'first':w.run('demo'),'replay':w.run('demo'),'audit':w.audit('demo')},indent=2))
