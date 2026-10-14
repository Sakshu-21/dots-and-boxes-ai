# 🎮 Dots & Boxes AI

An interactive **Dots & Boxes** game built with Python and Pygame, featuring an AI opponent powered by the **Minimax algorithm with Alpha-Beta Pruning**.

## ✨ Features

- 🎯 Play against an AI opponent.
- 🧠 AI decision-making using Minimax and Alpha-Beta Pruning.
- 📊 Live score tracking for the player and AI.
- 🔄 Extra turns when a player completes a box.
- 🎨 Interactive interface with highlighted moves, animations, and visual effects.
- 🏆 End-game screen with scores, winner announcement, and replay option.
- ⚙️ Adaptive search depth based on the number of remaining moves.

## 🛠️ Technologies Used

- **Language:** Python
- **Game Library:** Pygame
- **AI Algorithms:** Minimax, Alpha-Beta Pruning
- **Concepts:** Game Trees, Heuristic Evaluation, Decision-Making

## 🚀 Getting Started

### Prerequisites

Install Python 3.9 or later.

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Sakshu-21/dots-and-boxes-ai.git
   ```

2. Navigate to the project directory:

   ```bash
   cd dots-and-boxes-ai
   ```

3. Install Pygame:

   ```bash
   python -m pip install pygame
   ```

4. Run the game:

   ```bash
   python game.py
   ```

## 🎮 How to Play

1. Enter your initial when prompted.
2. Click on an available line between two dots to make a move.
3. Complete a box to earn a point and another turn.
4. Try to score more boxes than the AI.
5. When the game ends, choose to play again or quit.

## 🧠 How the AI Works

The AI uses **Minimax** to evaluate possible moves and choose a move based on the resulting game state. **Alpha-Beta Pruning** skips branches of the decision tree that cannot improve the current decision, reducing unnecessary search.

The AI also uses a heuristic evaluation function and adjusts its search depth according to the number of remaining moves.

## 📁 Project Structure

```text
dots-and-boxes-ai/
├── game.py
├── README.md
└── .gitignore
```

## 👩‍💻 Author

**Sakshi Vijay Rane**

GitHub: [@Sakshu-21](https://github.com/Sakshu-21)
