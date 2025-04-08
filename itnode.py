"""
3. ItNode
  - Waits for synchronization confirmation before starting.
  - Listen to move updates from all NotIt nodes and keep track of the global state. 
  - Choose a move strategically, chasing NotIt nodes using any simple heuristic/algorithm of your choice.
  - Publish move updates to GameNode every 0.5 seconds.
"""
import random
from logging import getLogger

from messages import freeze_t
from movement_monitor import MovementMonitor
from notitnode import NotItNode


logger = getLogger()


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
        # Some minor housekeeping: are there any new people we haven't seen?
        for nid in self.movement_monitor.get_last_movers():
            if nid not in self.tagged_nodes and nid != self.node_id:
                self.untagged_nodes.add(nid)
    
    def choose_move(self) -> tuple[int, int]:
        new_position = self.current_position
        nearest_node = self.find_nearest_node()
        if nearest_node is None:
            logger.warning("No untagged nodes found to seek. Moving at random.")
            return super().choose_move()

        # We have a nearest node. Convert dx and dy to be +1 or -1 each, then pick a direction at random.
        dx = ItNode.sign(nearest_node[0] - self.current_position[0])
        dy = ItNode.sign(nearest_node[1] - self.current_position[1])
        if random.random() > 0.5:
            new_position = (self.current_position[0]+dx, self.current_position[1])
        else:
            new_position = (self.current_position[0], self.current_position[1]+dy)

        return new_position
    
    def handle_freeze(self, channel, data):
        msg = freeze_t.decode(data)
        self.tagged_nodes.add(msg.id)
        if msg.id in self.untagged_nodes:
            self.untagged_nodes.remove(msg.id)

    def find_nearest_node(self) -> tuple[int, int] | None:
        """Find the nearest _in bounds_ node to the current position and returns it.
        If there are no untagged IDs, returns None."""
        if len(self.untagged_nodes) == 0:
            return None
        nearest_distance = self.board_shape[0] + self.board_shape[1] + 1  # Max possible distance.
        nearest_position = (0, 0)
        for node_id in self.untagged_nodes:
            node_pos = self.movement_monitor.get_node_position(node_id)
            if node_pos is None:
                logger.warning(f"Move monitor doesn't have a position for untagged node {node_id}")
                continue
            dx = node_pos[0] - self.current_position[0]
            dy = node_pos[1] - self.current_position[1]
            dist = abs(dx) + abs(dy)
            if dist < nearest_distance and self.position_in_bound(node_pos):
                nearest_distance = dist
                nearest_position = node_pos
        return nearest_position

    @staticmethod
    def sign(delta):
        if delta > 0:
            return 1
        elif delta < 0:
            return -1
        else:
            return 0
