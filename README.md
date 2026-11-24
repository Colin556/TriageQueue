# Triage Queue Manager

A production-quality priority queue system for hospital emergency unit patient intake. The system prioritizes patients by triage level (1=critical, 2=urgent, 3=standard) while maintaining strict FIFO ordering within each level.

## Overview

This project solves the hospital emergency unit whiteboard chaos problem:
- **Before**: Nurse manually writes names, calls them out, errors occur when updating concurrent
- **After**: Digital queue with correct priority and arrival-order logic

The system is built with clean architecture suitable for later integration into a larger medical IT platform.

## Features

✅ **Priority Queue Operations**
- Enqueue: Add new patient with automatic priority placement  
- Dequeue: Call next patient (removes from queue)
- Peek: See who's next without removing them
- List Queue: View all patients in order of attention
- Stats: See patient counts per triage level

✅ **Correct Triage Logic**
- Level 1 (critical) always served before levels 2 and 3
- Level 2 (urgent) always served before level 3
- Patients at the same level served in strict FIFO order
- New critical patient arriving during other patients' wait is immediately positioned first

✅ **Robust Design**
- Graceful error handling (empty queue, invalid input)
- Clear console interface with emoji feedback
- Uses only Python standard library (heapq, collections, datetime)

## Project Structure

```
TriageQueue/
├── DESIGN.md              # Architecture and design decisions
├── README.md              # This file
├── triage_queue.py        # Core queue implementation
├── cli.py                 # Command-line interface
└── test_triage_queue.py   # Unit tests (optional)
```

## Installation & Setup

### Requirements
- Python 3.7+
- No external dependencies (uses only standard library)

### Quick Start

1. **Clone or navigate to the project**
   ```bash
   cd /workspaces/TriageQueue
   ```

2. **Run the CLI**
   ```bash
   python cli.py
   ```

3. **You should see the menu**
   ```
   ============================================================
     HOSPITAL EMERGENCY UNIT - TRIAGE QUEUE MANAGER
   ============================================================
   
   Welcome to the Triage Queue Manager
   Type your choice (1-5) and press Enter
   ```

## Usage Guide

### Interactive Menu

Once you run `python cli.py`, you'll see this menu:

```
--- MENU ---
1) Add a new patient
2) Call next patient
3) View current queue
4) See queue statistics
5) Exit
```

### Operation Details

#### 1. Add a New Patient

```
--- ADD NEW PATIENT ---
Patient name: Alice Johnson
Triage level (1=Critical, 2=Urgent, 3=Standard): 2
✓ Alice Johnson added with triage level 2 [URGENT]
```

Triage levels:
- **1 = CRITICAL**: Life-threatening condition (heart attack, severe trauma)
- **2 = URGENT**: Serious but not immediately life-threatening (deep laceration, severe pain)
- **3 = STANDARD**: Non-emergency conditions (sprain, mild infection)

#### 2. Call Next Patient

```
--- CALL NEXT PATIENT ---
🔔 Calling: Alice Johnson (Level 2 [URGENT])
   Arrived at: 14:32:15
```

Removes patient from queue and displays their details.

#### 3. View Current Queue

```
--- CURRENT QUEUE ---
Next patient: Bob Smith (Level 1)
Arrived at: 14:35:22

All patients in queue (in order of attention):
------------------------------------------------------------
→ NEXT 1. Bob Smith              | Level 1 [CRITICAL  ] | 14:35:22
         2. Charlie Brown        | Level 2 [URGENT    ] | 14:30:10
         3. Diana Prince         | Level 2 [URGENT    ] | 14:31:45
         4. Eve Wilson           | Level 3 [STANDARD  ] | 14:25:00
------------------------------------------------------------
Total patients waiting: 4
```

Shows who's next and displays the entire queue in attention order.

#### 4. Queue Statistics

```
--- QUEUE STATISTICS ---
Critical (Level 1):  1 patient
Urgent (Level 2):   3 patients
Standard (Level 3): 2 patients
------------------------------------------------------------
Total waiting:      6 patients
```

Displays count of patients per triage level.

#### 5. Exit

Cleanly exits the program.

## Example Scenario

**Scenario: A critical patient arrives mid-queue**

Initial queue state:
```
1. Alice (Level 2, arrived 14:30)
2. Bob (Level 2, arrived 14:31)
3. Charlie (Level 3, arrived 14:25)
```

A critical patient "Dr. Emergency" arrives:
```
Patient name: Dr. Emergency
Triage level: 1
✓ Dr. Emergency added with triage level 1 [CRITICAL]
```

New queue state:
```
1. Dr. Emergency (Level 1, arrived 14:35)  ← Now first!
2. Alice (Level 2, arrived 14:30)          ← Pushed back
3. Bob (Level 2, arrived 14:31)
4. Charlie (Level 3, arrived 14:25)
```

**Key behavior**: Level 1 jumps to front automatically. Levels 2 and 3 maintain their FIFO order.

## Implementation Details

### Core Data Structure: Min-Heap with Tie-Breaking

Under the hood, `TriageQueue` uses Python's `heapq` module with tuples:

```python
(triage_level, sequence_counter, patient_object)
```

**Why this design:**
- **triage_level (1-3)**: Primary sort key ensures priority
- **sequence_counter**: Global counter assigns unique order across levels, ensuring FIFO within level
- **patient_object**: Actual patient data

**Performance:**
- Enqueue: O(log n) — heap insertion
- Dequeue: O(log n) — heap extraction
- Peek: O(1) — access top without removal
- List Queue: O(n) — iterate all patients
- Stats: O(n) — count per level

See [DESIGN.md](DESIGN.md) for full architectural details.

## Testing (Optional)

Create a test file `test_triage_queue.py`:

```python
from triage_queue import Patient, TriageQueue, QueueEmptyError
from datetime import datetime

def test_level_priority():
    """Level 1 patients are always served first."""
    queue = TriageQueue()
    queue.enqueue(Patient("Alice", 2, datetime.now()))
    queue.enqueue(Patient("Bob", 1, datetime.now()))
    assert queue.peek().name == "Bob"
    print("✓ test_level_priority passed")

def test_fifo_within_level():
    """FIFO ordering within same level."""
    queue = TriageQueue()
    p1 = Patient("Alice", 2, datetime.now())
    p2 = Patient("Bob", 2, datetime.now())
    queue.enqueue(p1)
    queue.enqueue(p2)
    assert queue.dequeue().name == "Alice"
    assert queue.dequeue().name == "Bob"
    print("✓ test_fifo_within_level passed")

def test_empty_queue():
    """Empty queue raises error."""
    queue = TriageQueue()
    try:
        queue.dequeue()
        assert False, "Should raise QueueEmptyError"
    except QueueEmptyError:
        print("✓ test_empty_queue passed")

def test_preemption():
    """Critical patient arriving preempts lower levels."""
    queue = TriageQueue()
    queue.enqueue(Patient("Alice", 2, datetime.now()))
    queue.enqueue(Patient("Bob", 3, datetime.now()))
    queue.enqueue(Patient("Charlie", 1, datetime.now()))
    assert queue.dequeue().name == "Charlie"
    assert queue.dequeue().name == "Alice"
    assert queue.dequeue().name == "Bob"
    print("✓ test_preemption passed")

if __name__ == "__main__":
    test_level_priority()
    test_fifo_within_level()
    test_empty_queue()
    test_preemption()
    print("\nAll tests passed! ✓")
```

Run tests:
```bash
python test_triage_queue.py
```

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Dequeue on empty queue | Raises `QueueEmptyError` with message |
| Peek on empty queue | Raises `QueueEmptyError` with message |
| Invalid triage level (not 1-3) | Rejects input, prompts again |
| Empty patient name | Rejects input, prompts again |
| Multiple critical patients | Served in arrival order |
| Invalid menu choice | Shows warning, prompts again |

## Real-World Production Considerations

This system could be extended for production use:

1. **Database Storage**: Replace in-memory heap with SQL database (SQLite → PostgreSQL)
2. **Concurrency**: Add thread locks for multi-worker scenarios (see DESIGN.md)
3. **API Layer**: Expose as REST API (Flask/FastAPI)
4. **Persistence**: Store queue state to recover from crashes
5. **Analytics**: Track wait times, peak hours, service level metrics
6. **Integration**: Connect with EHR (Electronic Health Records) system
7. **UI**: Web dashboard or mobile app for staff

## Troubleshooting

**Program won't start**
```bash
# Ensure Python 3.7+ installed
python --version

# Try explicit Python 3
python3 cli.py
```

**Queue appears empty but I added patients**
- Confirm you pressed Enter after each input
- Check you entered valid triage levels (1, 2, or 3)

**Can't add patient (name rejected)**
- Name field cannot be empty; type at least one character

## Files Reference

| File | Purpose |
|------|---------|
| `triage_queue.py` | Core queue implementation; can be imported into other projects |
| `cli.py` | Menu-driven CLI; entry point for end users |
| `DESIGN.md` | Architecture, data structure rationale, concurrency notes |
| `test_triage_queue.py` | Unit tests demonstrating correctness |
| `README.md` | This file |

## License

This is a demonstration project for educational and interview purposes.

## Author Notes

Built to solve a real-world problem: emergency unit patient intake. The design is intentionally clean and extensible so it can be:
- Discussed in technical interviews (data structures, algorithms, concurrency)
- Integrated into production hospital systems
- Extended with additional features (persistence, APIs, analytics)

The heap-based approach with sequence counters elegantly solves the dual requirement of priority ordering and FIFO within levels, without manual sorting or multiple data structures.

---

**Questions or improvements?** This system is designed to evolve as requirements grow.
