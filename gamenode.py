"""
1. GameNode 
  - Listens to position updates from It and NotIt nodes. Keeps track of the global states in a NxM board.
  - If the It node and NotIt node are in the same square, send a message to the NotIt node to freeze. 
  - Visually represents the game state using a simple GUI.
  - Keep track of the number of NotIt nodes which have been frozen. If all NotIt nodes are frozen, then end the game. 
"""

import lcm
import threading
from enum import IntEnum

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t
from node import Node


class GameNode(Node):
    def __init__(self, board_shape: tuple[int, int], node_count: int):
        super().__init__()
        assert board_shape[0] > 0 and board_shape[1] > 0
        self.board_shape = board_shape
        # We could track the board bounds as an array of entries:
        #self.board_state = [BoardOccupant.Empty] * board_shape[0] * board_shape[1]
        # But it's easier for book keeping if we have a map of ID -> position and Position -> IDs.
        self.node_to_position = dict()
        self.position_to_nodes = list()  # A 2D array of [x+y*width] -> list of IDs.
        self.node_count = node_count
        self.node_reports = 0  # Have all the workers chimed in?
        for i in range(self.board_shape[0]*self.board_shape[1]):
            self.position_to_nodes.append(list())
        print("Game Node Initialized")

    def on_start(self):
        self.subscribe(Channels.REPORT_READY, self.process_ready_report)
        self.subscribe(Channels.REPORT_MOVE, self.process_move_report)
        self.node_reports = 0
        print("Game Node Started")
    
    def run(self):
        i = 100000
        while i > 0:
            i -= 1
    
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
        if self.node_reports == self.node_count:
            print("All nodes have reported -- starting game.")
            msg = begin_t()
            self.publish(Channels.BEGIN_GAME, msg)
    
    def process_move_report(self, channel, data):
        print("Move report")
