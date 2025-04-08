import unittest

from notitnode import NotItNode

class TestNode(unittest.TestCase):

    def test_not_it_node(self):
        n = NotItNode(1, start_position=(1, 1), board_shape=(3, 3), move_frequency=1.0)
        self.assertEqual(n.current_position, (1, 1))
        target = n.choose_move()
        print(target)
        self.assertNotEqual(target, (1,1))

if __name__ == '__main__':
    unittest.main()