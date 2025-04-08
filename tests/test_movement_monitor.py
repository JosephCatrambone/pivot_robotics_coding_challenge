#!/usr/bin/env python -m unittest tests.test_movement_monitor.TestMovementMonitor

import unittest

from movement_monitor import MovementMonitor

class TestMovementMonitor(unittest.TestCase):

    def test_move(self):
        mm = MovementMonitor()
        mm.set_node_position(1, (1, 2))
        self.assertEqual(mm.get_node_position(1), (1, 2))
        id_list = mm.get_nodes_at_position((1, 2))
        self.assertEqual(id_list, [1])

    def test_init(self):
        mm = MovementMonitor()
        mm.set_node_position(3, (3, 4), clear_previous=False)
        self.assertEqual(mm.get_node_position(3), (3, 4))
    
    def test_different_start_positions(self):
        mm = MovementMonitor()
        mm.set_node_position(1, (5, 6), clear_previous=False)
        mm.set_node_position(3, (0, 0), clear_previous=False)
        self.assertNotEqual(mm.get_node_position(1), mm.get_node_position(3))
    
    def test_last_move_update_list(self):
        mm = MovementMonitor()
        mm.set_node_position(1, (0, 0))
        last_moved = mm.get_last_movers()
        self.assertEqual(last_moved, {1})
        last_moved = mm.get_last_movers()
        self.assertEqual(last_moved, set())

if __name__ == '__main__':
    unittest.main()