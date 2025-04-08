# Distributed Freeze Tag Game Challenge

This coding challenge involves implementing a distributed real-time Freeze Tag game using multiple agents that communicate over a network. One agent is designated as "It" and the rest are "NotIt" agents. The "It" agent's goal is to chase and freeze all "NotIt" agents. This challenge evaluates your ability to write clean, well-structured code and your understanding of distributed system concepts such as message passing and coordination across nodes.
What You Will Build: A Python-based simulation of Freeze Tag with distributed agents communicating via a publish/subscribe mechanism using LCM (Lightweight Communications and Marshalling). The game continues until all "NotIt" agents have been frozen by the "It" agent.

## Skills Assessed:
Clean coding practices (readability, modularity, proper resource management)
Distributed systems fundamentals (concurrent agents, network communication, coordination)

## Implementation Details
You will use LCM for communication between agents. We provide boilerplate code (node.py) to help structure your implementation. Based on this, you will implement the following nodes in the system, which inherit the Node class from node.py:

## Components
1. GameNode 
  - Listens to position updates from It and NotIt nodes. Keeps track of the global states in a NxM board.
  - If the It node and NotIt node are in the same square, send a message to the NotIt node to freeze. 
  - Visually represents the game state using a simple GUI.
  - Keep track of the number of NotIt nodes which have been frozen. If all NotIt nodes are frozen, then end the game. 
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
3. ItNode
  - Waits for synchronization confirmation before starting.
  - Listen to move updates from all NotIt nodes and keep track of the global state. 
  - Choose a move strategically, chasing NotIt nodes using any simple heuristic/algorithm of your choice.
  - Publish move updates to GameNode every 0.5 seconds.

To ensure fair and synchronized gameplay, implement logic to guarantee that all nodes have successfully started and confirmed readiness via LCM before gameplay begins. Agents must only start moving after synchronization confirmation is received.

## Game Initialization
The simulation should run using the command-line arguments:

`python game.py --width N --height M --num-not-it P --positions x1 y1 x2 y2 ... x_it y_it`

Example:

`python game.py --width 20 --height 15 --num-not-it 2 3 5 10 12 0 0`

(Initializes a 20x15 board with two "NotIt" agents at (3,5), (10,12), and one "It" agent at (0,0))

To coordinate launching and shutdown of the nodes, we share game.py which has some boilerplate code showing how to coordinate the launch and shutdown of a node. Please fill that in to enable the simulation to launch according to the interface defined above. Make sure that on exit all the nodes exit correctly and all resources are correctly released.

## Dockerization
Your solution must be containerized using Docker:
- Provide a Dockerfile specifying all dependencies and necessary setup instructions.
- Ensure your simulation can be executed seamlessly within the Docker container.
- Clearly document Docker commands to build and run your solution.
Example:
`docker build -t freeze-tag .`
`docker run -it --rm freeze-tag --width 20 --height 15 --num-not-it 2 3 5 10 12 0 0`

## Testing and Submission
- Ensure each node type (GameNode, "It", and "NotIt") runs concurrently on a single machine.
- Submit complete Python source code, Dockerfile and a README on how to run the simulation.

## Technical Requirements
- Language: Python
- Communication: Use LCM for messaging via a publish/subscribe model, node.py has boilerplate code to get you started. 
- All agents run concurrently as separate processes on a single machine.
- Clear, structured, and modular Python code.
- Graceful shutdown upon receiving a game-over message or termination signals with no hanging processes. 
## Challenge Guidelines
- For any questions or clarifications, please feel free to email at siddharth@pivotrobotics.com. 
- The use of any and all internet resources (including AI tools) is allowed and even encouraged for this challenge. 
