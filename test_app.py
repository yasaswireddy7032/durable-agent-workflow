import unittest
from app import *

class WorkflowTests(unittest.TestCase):
    def test_approval_gate(self):
        w=Workflow();w.submit('x',{})
        with self.assertRaises(PermissionError):w.run('x')
    def test_replay(self):
        w=Workflow();w.submit('x',{});w.approve('x');self.assertEqual(w.run('x'),w.run('x'));self.assertEqual(w.audit('x').count('completed'),1)
    def test_conflicting_key(self):
        w=Workflow();w.submit('x',{})
        with self.assertRaises(ValueError):w.submit('x',{'other':1})
    def test_restart(self):
        import tempfile,os
        with tempfile.TemporaryDirectory() as d:
            p=os.path.join(d,'workflow.db');a=Workflow(p);a.submit('x',{});a.approve('x');a.db.close()
            b=Workflow(p);self.assertEqual(b.run('x')['state'],'completed');b.db.close()
    def test_rollback(self):
        w=Workflow();w.submit('x',{'items':[1]});w.approve('x')
        with self.assertRaises(ValueError):w.run('x')
        self.assertEqual(w.get('x')['state'],'approved')

if __name__ == '__main__': unittest.main()
