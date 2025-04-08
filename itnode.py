"""
3. ItNode
  - Waits for synchronization confirmation before starting.
  - Listen to move updates from all NotIt nodes and keep track of the global state. 
  - Choose a move strategically, chasing NotIt nodes using any simple heuristic/algorithm of your choice.
  - Publish move updates to GameNode every 0.5 seconds.
"""
import threading
import time
import random

from channels import Channels
from messages import freeze_t, moved_t
from movement_monitor import MovementMonitor
from notitnode import NotItNode


class ItNode(NotItNode):
    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int], move_frequency: float):
        super().__init__(
            node_id=node_id, 
            start_position=start_position, 
            board_shape=board_shape, 
            move_frequency=move_frequency
        )
        self.movement_monitor = MovementMonitor()
        self.tagged_nodes = set()
        self.untagged_nodes = set()
    
    def on_start(self):
        super().on_start()
        self.movement_monitor.register_listeners(self.lc)
    
    def tick(self):
        self.frozen = False
        # Some minor housekeeping: are there any new people we haven't seen?
        for nid in self.movement_monitor.get_last_movers():
            if nid not in self.tagged_nodes:
                self.untagged_nodes.add(nid)
    
    def choose_move(self) -> tuple[int, int]:
        # Chase the nearest node:
        nearest_distance = self.board_shape[0]*self.board_shape[1]  # This will be greater than the largest dist possible.
        nearest_id = 0
        movement_direction = (0, 0)
        for nid in self.untagged_nodes:
            if nid == self.node_id:
                continue
            node_position = self.movement_monitor.get_node_position(nid)
            if node_position:
                dx = node_position[0] - self.current_position[0]
                dy = node_position[1] - self.current_position[1]
                if abs(dx)+abs(dy) < nearest_distance:
                    nearest_id = nid
                    movement_direction = (dx, dy)
                    nearest_distance = abs(dx)+abs(dy)
        new_position = (
            self.current_position[0] + movement_direction[0], 
            self.current_position[1] + movement_direction[1]
        )
        
        # Mild sanity check.  This should never happen because we're always in bounds, but...
        assert new_position[0] >= 0 and new_position[0] < self.board_shape[0]
        assert new_position[1] >= 0 and new_position[1] < self.board_shape[1]

        # TODO: Need to make sure this doesn't keep moving towards the nearest _already tagged_.
        # TODO: Listen and remove from tagged?

        return new_position