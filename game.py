# game.py
import multiprocessing
import sys
from logging import getLogger, DEBUG

import argparse

from gamenode import GameNode
from itnode import ItNode
from notitnode import NotItNode


NOT_IT_MOVE_SPEED = 1.0
IT_MOVE_SPEED = 0.5
logger = getLogger()


parser = argparse.ArgumentParser()
parser.add_argument("--width", type=int, required=True)
parser.add_argument("--height", type=int, required=True)
parser.add_argument("--num-not-it", type=int, required=True)
parser.add_argument("--positions", type=int, nargs="*", required=False)  # Argparse does not allow something to be both named and positional
parser.add_argument("posits", type=int, nargs="?", default=None)


def main():
    """
    Main function to parse arguments and launch the required nodes.
    """
    # Parse and sanity-check arguments:
    args = parser.parse_args()
    width = args.width
    height = args.height
    num_not_it = args.num_not_it
    positions = args.positions
    if not positions:
        positions = parser.posits

    if len(positions) % 2 != 0:
        print("Positions got an odd number of arguments and can't be mapped to (x,y) pairs.")
        sys.exit(-1)
    
    # If we need more than 254 hiders and 1 seeker we need to change the ID to a multi-byte int.
    assert num_not_it < 254, "Only 255 total nodes are supported at this time."

    # Make a list of tuples for positions.
    positions = [p for p in zip(positions[0::2], positions[1::2])]
    it_position = positions[-1]
    positions = positions[:-1]

    if len(positions) != num_not_it:
        print(f"{num_not_it} 'not its' specified, but only got {len(positions)} positions. Perhaps you forgot the last position is the 'it'?")
        sys.exit(-1)
    
    print(f"Running with parameters:\nWidth:{width}\nHeight:{height}\nIt Position:{it_position}\nPositions:{positions}")
    run(width, height, positions, it_position)


def run(width: int, height: int, not_it_positions: list[tuple[int, int]], it_position:tuple[int, int]):
    """
    Spin up the main game node first so that it can receive commands.
    Spin up each of the not-it nodes.
    Spin up the 'it' node.
    Wait for the main game node to terminate.
    """
    it_id = len(not_it_positions)+1
    processes = list()

    logger.info("Spawning GameNode")
    game_node = GameNode(board_shape=(width, height), node_count=len(not_it_positions), it_id=it_id)
    main_node_process = multiprocessing.Process(target=game_node.launch_node, name="GameNode")
    processes.append(main_node_process)

    # Spin up the seeker so it can listen as things report spawning.
    logger.info("Spawning 'it' node")
    it_node = ItNode(node_id=it_id, start_position=it_position, board_shape=(width, height), move_frequency=IT_MOVE_SPEED)
    it_process = multiprocessing.Process(target=it_node.launch_node, name="Seeker")
    processes.append(it_process)

    # Start up the 'not its'.
    logger.info("Spawning 'not it' nodes")
    for idx, pos in enumerate(not_it_positions):
        not_it_node = NotItNode(node_id=idx, start_position=pos, board_shape=(width, height), move_frequency=NOT_IT_MOVE_SPEED)
        not_it_process = multiprocessing.Process(target=not_it_node.launch_node, name=f"Hider{idx}")
        processes.append(not_it_process)

    logger.info("Starting all processes")
    for p in processes:
        p.start()

    logger.info("Awaiting GameNode completion")
    main_node_process.join()


if __debug__:
    logger.setLevel(DEBUG)


if __name__ == "__main__":
    main()
