#!/usr/bin/env python -m unittest tests.test_movement_monitor.TestMovementMonitor
import copy

from channels import Channels
from messages import moved_t


class MovementMonitor:
    def __init__(self):
        # We could track the board bounds as an array of entries:
        #self.board_state = [BoardOccupant.Empty] * board_shape[0] * board_shape[1]
        # But it's easier for book keeping if we have a map of ID -> position and Position -> IDs.
        self.node_to_position = dict()
        self.position_to_nodes = dict()
    
    def set_node_position(self, node_id: int, position: tuple[int, int], clear_previous: bool = True):
        if clear_previous:
            previous_position = self.node_to_position.get(node_id)
            if previous_position and previous_position in self.position_to_nodes:
                self.position_to_nodes[previous_position].remove(node_id)
                if len(self.position_to_nodes[previous_position]) == 0:
                    del self.position_to_nodes[previous_position]
        # Add the new entry:
        self.node_to_position[node_id] = position
        if position not in self.position_to_nodes:
            self.position_to_nodes[position] = list()
        self.position_to_nodes[position].append(node_id)
    
    def get_nodes_at_position(self, position: tuple[int, int]) -> list[int]:
        if position not in self.position_to_nodes:
            return []
        return copy.copy(self.position_to_nodes[position])
    
    def get_node_position(self, node_id: int) -> tuple[int, int] | None:
        return self.node_to_position.get(node_id)

    # LC Interface:
    def register_listeners(self, lc_ref):
        # Call this in on_start in a node.
        lc_ref.subscribe(Channels.REPORT_MOVE, self.process_move_report)

    def process_move_report(self, channel, data):
        msg = moved_t.decode(data)
        self.set_node_position(msg.id, msg.new_position)
