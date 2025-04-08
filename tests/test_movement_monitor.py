import unittest

from movement_monitor import MovementMonitor

class TestMovementMonitor(unittest.TestCase):

    def test_move(self):
        mm = MovementMonitor()
        mm.set_node_position(1, (1, 2))
        self.assertEqual(mm.get_node_position(1), (1, 2))
        id_list = mm.get_nodes_at_position((1, 2))
        self.assertEqual(id_list, [1])

if __name__ == '__main__':
    unittest.main()