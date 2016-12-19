import unittest

from pynusmv             import init
from pynusmv.utils       import StdioFile 
from pynusmv.node        import Node
from pynusmv.parser      import parse_simple_expression  
from pynusmv.collections import NodeList


class TestNodeList(unittest.TestCase):
    
    def setUp(self):
        init.init_nusmv()
        
    def tearDown(self):
        init.deinit_nusmv()
        
    def node_from_expr(self, expr):
        return Node.from_ptr(parse_simple_expression(expr))
    
    def test_empty(self):
        lst = NodeList.empty()
        self.assertEqual(len(lst), 0, "lst should be empty")
        
    
    def test_from_list(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        lst = [a, b, c]
        nlst= NodeList.from_list(lst)
        
        self.assertTrue(a in nlst)
        self.assertTrue(b in nlst)
        self.assertTrue(c in nlst)
        
        self.assertEqual(nlst[0], a)
        self.assertEqual(nlst[1], b)
        self.assertEqual(nlst[2], c)
    
    def test_to_list(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        nlst= list(NodeList.from_list([a, b, c]))
        self.assertListEqual(nlst, [a, b, c])

    def test_copy(self):
        a = self.node_from_expr("a = 12")
        
        nlst= NodeList.empty()
        cpy = nlst.copy()
        
        self.assertTrue(a not in cpy)
        
        nlst.append(a)
        cpy = nlst.copy()
        
        self.assertTrue(a in cpy)
        

    def test_append(self):
        nlst= NodeList.empty()
         
        # append on empty works
        a = self.node_from_expr("a = 12")
        self.assertTrue(a not in nlst)
        nlst.append(a)
        self.assertTrue(a in nlst)
        self.assertEqual(a, nlst[0])
         
        # append on non empty works
        b = self.node_from_expr("b = 23")
        self.assertTrue(b not in nlst)
        nlst.append(b)
        self.assertTrue(b in nlst)
        self.assertEqual(b, nlst[1])
        
    def test_prepend(self):
        nlst= NodeList.empty()
         
        # append on empty works
        a = self.node_from_expr("a = 12")
        self.assertTrue(a not in nlst)
        nlst.prepend(a)
        self.assertTrue(a in nlst)
        self.assertEqual(a, nlst[0])
         
        # append on non empty works
        b = self.node_from_expr("b = 23")
        self.assertTrue(b not in nlst)
        nlst.prepend(b)
        self.assertTrue(b in nlst)
        self.assertEqual(b, nlst[0])
        self.assertEqual(a, nlst[1])

    def test_length(self):
        nlst= NodeList.empty()
        self.assertEqual(0, len(nlst))
         
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        nlst= NodeList.from_list([a, b, c])
        self.assertEqual(3, len(nlst))

    def test_reverse(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        nlst= NodeList.from_list([a, b, c])
        nlst.reverse()
        self.assertEqual(3, len(nlst))
        self.assertEqual(c, nlst[0])
        self.assertEqual(b, nlst[1])
        self.assertEqual(a, nlst[2])
        
    def test_extend_non_unique(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        beg = NodeList.from_list([a])
        end = NodeList.from_list([a, b,c])
        
        
        beg.extend(end)
        self.assertEquals(beg[0], a)
        self.assertEquals(beg[1], a)
        self.assertEquals(beg[2], b)
        self.assertEquals(beg[3], c)
        
    def test_extend_unique(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        beg = NodeList.from_list([a])
        end = NodeList.from_list([a, b,c])
        
        
        beg.extend(end, unique=True)
        self.assertEquals(beg[0], a)
        self.assertEquals(beg[1], b)
        self.assertEquals(beg[2], c)
        
    def test_contains(self):
        a   = self.node_from_expr("a = 1")
        nlst= NodeList.empty()
        self.assertTrue(a not in nlst)
        nlst.append(a)
        self.assertTrue(a in nlst)
        
    def test_count(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        nlst= NodeList.from_list([a, a, b])
        self.assertEqual(nlst.count(a), 2)
        self.assertEqual(nlst.count(b), 1)
        self.assertEqual(nlst.count(c), 0)

    def test_getitem(self):
        a   = self.node_from_expr("a = 1")
        lst = NodeList.empty()
        try: 
            lst[0]
        except KeyError:
            self.assertTrue(True)
              
        lst.append(a)
        self.assertEqual(a, lst[0])
        
    def test_delitem(self):
        a   = self.node_from_expr("a = 1")
        lst = NodeList.from_list([a])
        self.assertEqual(1, len(lst))
        self.assertTrue(a in lst)
          
        del lst[0]
        self.assertTrue(a not in lst)
        self.assertEqual(0, len(lst))

    def test_iter(self):    
        nlst= NodeList.empty()
        a = self.node_from_expr("a = 1")
        b = self.node_from_expr("b = 2")
        c = self.node_from_expr("c = 3")
        nlst.append(a)
        nlst.append(b)
        nlst.append(c) 
        
        lst = [a,b,c]
        out = []
        for v in nlst:
            out.append(v)
            
        self.assertListEqual(out, lst)
        
    def test_print_nodes(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        nlst= NodeList.from_list([a, b, c])
        
        nlst.print_nodes(StdioFile.stdout())
        
    def test_insert_before(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        
        # empty
        nlst= NodeList.empty()
        nlst.insert_before(iter(nlst), a)
        self.assertEqual(1, len(nlst))
        self.assertEqual(a, nlst[0])
        
        # filled
        it = iter(nlst)
        it.__next__()
        nlst.insert_before(it, b)
        self.assertEqual(2, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(b, nlst[1])

        # in the middle
        it = iter(nlst)
        it.__next__()
        nlst.insert_before(it, c)
        self.assertEqual(3, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(c, nlst[1])
        self.assertEqual(b, nlst[2])

    def test_insert_after(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        
        # empty
        nlst= NodeList.empty()
        with self.assertRaises(ValueError):
            nlst.insert_after(iter(nlst), a)
        
        # filled
        nlst.append(a)
        it = iter(nlst)
        nlst.insert_after(it, b)
        self.assertEqual(2, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(b, nlst[1])
        
        # at end
        it = iter(nlst)
        it.__next__()
        nlst.insert_after(it, c)
        self.assertEqual(3, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(b, nlst[1])
        self.assertEqual(c, nlst[2])
    
    def test_insert_at(self):
        a   = self.node_from_expr("a = 1")
        b   = self.node_from_expr("b = 2")
        c   = self.node_from_expr("c = 3")
        
        # empty
        nlst= NodeList.empty()
        nlst.insert_at(0, a)
        self.assertEqual(1, len(nlst))
        self.assertEqual(a, nlst[0])
        
        # filled
        nlst.insert_at(1, b)
        self.assertEqual(2, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(b, nlst[1])

        # in the middle
        nlst.insert_at(1, c)
        self.assertEqual(3, len(nlst))
        self.assertEqual(a, nlst[0])
        self.assertEqual(c, nlst[1])
        self.assertEqual(b, nlst[2])
        
