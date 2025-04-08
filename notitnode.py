"""
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
"""
import random
import time

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t

from playernode import PlayerNode


class NotItNode(PlayerNode):

    def tick(self):
        pass

    def choose_move(self) -> tuple[int, int]:
        """
        Returns the next position that this node should assume.
        This is not the DELTA of the position but the absolute world position.
        """
        candidate_moves = list()
        for (dx, dy) in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            next_x = self.current_position[0] + dx
            next_y = self.current_position[1] + dy
            if (next_x >= 0 and next_x < self.board_shape[0] and 
                    next_y >= 0 and next_y < self.board_shape[1]):
                candidate_moves.append((next_x, next_y))
        if len(candidate_moves) == 0:
            # If the board is too small we may have no options.
            print(f"Candidate moves list is empty for node id {self.node_id}.  Pos: {self.current_position}  Board shape: {self.board_shape}")
            next_position = self.current_position
        else:
            next_position = random.choice(candidate_moves)
        return next_position
