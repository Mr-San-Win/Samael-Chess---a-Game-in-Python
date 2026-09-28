---

# **Sam@el’s Chess**

### *A Single-File Python Chess Engine with Tkinter GUI*



---

## **Project Summary**

**Sam@el’s Chess** is a complete chess application built in **Python** using **Tkinter**, implemented entirely in a **single .py file** while maintaining clean internal modularity.
It provides a full chess engine, multiple game modes, rule enforcement, and a multi-page user interface suitable for academic submission and portfolio demonstration.

This project implements professional **Object-Oriented Programming**, encapsulated rule logic, and two distinct AI levels.

---

## **Feature Overview**

### **Gameplay**

| Feature           | Description                           |
| ----------------- | ------------------------------------- |
| PvP Mode          | Local player vs player                |
| Human vs AI       | Beginner-friendly & strong AI options |
| Move Highlighting | Shows legal moves for selected piece  |
| Move History      | Real-time log of moves                |
| Captured Pieces   | Visual display of taken pieces        |
| Time Controls     | Unlimited, 5, 10, 30 minutes          |

### **Rule Engine**

| Rule                    | Status             |
| ----------------------- | ------------------ |
| Castling                | Fully implemented  |
| En Passant              | Supported          |
| Pawn Promotion          | Automatic prompt   |
| Check Detection         | Fully validated    |
| Stalemate / Checkmate   | Handled            |
| Illegal Move Prevention | Strict enforcement |

### **User Interface**

* Multi-page Tkinter navigation
* Dark-mode themed layout
* Responsive square rendering
* Scrollable educational content
* Precise board interaction design

---

## **Architecture**

### **Class Hierarchy**

```
ChessGame        # Core game engine
Piece            # Base class
 ├── Pawn
 ├── Knight
 ├── Bishop
 ├── Rook
 ├── Queen
 └── King
```

### **Design Principles Used**

* **Inheritance** for piece specialization
* **Polymorphism** through `can_move()` overrides
* **Composition**: `ChessGame` owns board + rules
* **Encapsulation** of internal game state
* **Dictionary usage** for castling rights, promotions, UI routing
* **Exception handling** for invalid states

### **Internal Structure (Single-File Project)**

The `.py` file is organized into logical sections:

```
1. Constants & Utilities
2. Piece Classes
3. ChessGame Engine
4. Move Validator
5. AI Algorithms
6. Tkinter UI Pages
7. Application Entry Point
```

---

## **AI System**

### **Club-Level AI**

* Chooses randomly from all legal moves
* Low-complexity, beginner friendly

### **Strong AI**

* Material-based evaluation
* Move scoring heuristics
* Prioritizes advantageous positions

---

## **Installation & Execution**

### **Requirements**

* Python **3.11+**
* Tkinter (included with Windows/macOS)

### **Run the Application**

```bash
python "Python Project.py"
```

---

## **Build a Standalone Executable (Windows)**

```bash
pip install pyinstaller
pyinstaller --onefile "Python Project.py"
```

Executable will appear in:

```
/dist/
```

---

## **License**

This project is intended for academic, personal, and educational use.

---

## **Author**

**San Win**
Software Engineering Student — KMITL, Thailand

---

