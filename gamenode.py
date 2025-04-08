"""
1. GameNode 
  - Listens to position updates from It and NotIt nodes. Keeps track of the global states in a NxM board.
  - If the It node and NotIt node are in the same square, send a message to the NotIt node to freeze. 
  - Visually represents the game state using a simple GUI.
  - Keep track of the number of NotIt nodes which have been frozen. If all NotIt nodes are frozen, then end the game. 
"""

import lcm
import threading
import time

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t
from movement_monitor import MovementMonitor
from node import Node


MIN_SLEEP_TIME = 0.0001  # Chosen for compatibility. A time of zero doesn't always yield.


class GameNode(Node):
    def __init__(self, board_shape: tuple[int, int], node_count: int, it_id: int):
        super().__init__()
        assert board_shape[0] > 0 and board_shape[1] > 0
        self.board_shape = board_shape
        self.movement_monitor = MovementMonitor()
        self.node_count = node_count
        self.node_reports = 0  # Have all the workers chimed in?
        self.it_id = it_id  # Used to check when "it" has tagged a node.
        self.untagged_nodes = set()
        print("Game Node Initialized")

    def on_start(self):
        self.subscribe(Channels.REPORT_READY, self.process_ready_report)
        self.movement_monitor.register_listeners(self.lc)
        self.node_reports = 0
        print("Game Node Started")
    
    def run(self):
        while self.untagged_nodes or self.node_reports < self.node_count:
            time.sleep(1)
            self.handle_freezing()
            self.render_tui()
            
    def handle_freezing(self):
        it_position = self.movement_monitor.get_node_position(self.it_id)
        if it_position is None:
            return
        # Find other nodes tagged by it.
        newly_tagged_nodes = self.movement_monitor.get_nodes_at_position(it_position)
        for t in newly_tagged_nodes:
            if t in self.untagged_nodes:
                msg = freeze_t()
                msg.id = t
                msg.position = it_position
                self.publish(Channels.FREEZE, msg)
                self.untagged_nodes.remove(t)
    
    def render_tui(self):
        it_position = self.movement_monitor.get_node_position(self.it_id)
        if it_position is None:
            print("Awaiting 'it' to register.")
            return
        print("-"*20)
        for y in range(0, self.board_shape[1]):
            for x in range(0, self.board_shape[0]):
                if x == it_position[0] and y == it_position[1]:
                    print("X", end = " ")
                else:
                    count = len(self.movement_monitor.get_nodes_at_position((x, y)))
                    if count == 0:
                        print("_", end = " ")
                    else:
                        print(count, end=" ")
            print()
        print("-"*20)
        print(f"Untagged: {self.untagged_nodes}")

    def on_stop(self):
        # Do we want to reserve 'on stop' for other kinds of cleanup?
        # We could make this the last step in the run.
        msg = gameover_t()
        self.publish(Channels.STOP_GAME, msg)
        print("Game Node stopping - cleanup")

    def process_ready_report(self, channel, data):
        print("Ready report")
        msg = report_ready_t.decode(data)
        self.node_reports += 1
        
        # The 'it' doesn't need to be tagged:
        if msg.id != self.it_id:
            self.untagged_nodes.add(msg.id)
        
        # Check if we're ready.
        if self.node_reports == self.node_count:
            print(f"All nodes ({self.untagged_nodes}) have reported -- starting game.")
            msg = begin_t()
            self.publish(Channels.BEGIN_GAME, msg)
