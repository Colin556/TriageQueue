# Quick Start Guide - Triage Queue Manager

## 🚀 Get Started in 30 Seconds

### 1. Run the Interactive CLI
```bash
python cli.py
```

This opens the main menu where you can:
- Add patients
- Call the next patient
- View the queue
- See statistics
- Exit

### 2. Run Automated Demo (No Input Required)
```bash
python demo.py
```

Shows the system in action with a realistic hospital scenario.

### 3. Run All Tests
```bash
# Unit tests (13 comprehensive tests)
python test_triage_queue.py

# Integration tests
python test_integration.py
```

## 📁 Project Files

| File | Purpose | Run With |
|------|---------|----------|
| `triage_queue.py` | Core priority queue implementation | (import in other code) |
| `cli.py` | Interactive menu interface | `python cli.py` |
| `demo.py` | Automated demonstration | `python demo.py` |
| `test_triage_queue.py` | Unit tests (13 tests) | `python test_triage_queue.py` |
| `test_integration.py` | Integration tests | `python test_integration.py` |
| `README.md` | Full documentation | (read in editor) |
| `DESIGN.md` | Architecture & design decisions | (read in editor) |

## 💡 What This System Does

✅ **Manages patient queue with priority levels:**
- Level 1: CRITICAL (served first)
- Level 2: URGENT (served after critical)
- Level 3: STANDARD (served last)

✅ **Maintains FIFO ordering within each level:**
- Among level 2 patients, earlier arrivals are served first
- No matter the order, priority level always determines position

✅ **Handles edge cases gracefully:**
- Empty queue operations don't crash
- Invalid input is rejected with clear feedback
- Timestamps tracked for auditing

## 🎯 Example Interaction

```
1) Add a new patient
2) Call next patient
3) View current queue
4) See queue statistics
5) Exit
------

Your choice: 1

--- ADD NEW PATIENT ---
Patient name: Alice Johnson
Triage level (1=Critical, 2=Urgent, 3=Standard): 2
✓ Alice Johnson added with triage level 2 [URGENT]

Your choice: 2

--- CALL NEXT PATIENT ---
🔔 Calling: Alice Johnson (Level 2 [URGENT])
   Arrived at: 14:32:15
```

## 🔍 Key Features Demonstrated

### Priority Preemption
If a critical patient arrives while others are waiting, they jump to the front:
```
Queue before: [Urgent Alice, Standard Bob]
Add Critical Charlie
Queue after: [Critical Charlie, Urgent Alice, Standard Bob]
```

### FIFO Fairness
Patients at the same level are served in order:
```
Queue: [Critical A, Urgent B (arrived 14:00), Urgent C (arrived 14:05), Standard D]
Call order: A → B → C → D
(B before C because B arrived first)
```

### No Crashes
Trying to call from an empty queue gives a friendly message:
```
Cannot dequeue: queue is empty
```

## 📊 Statistics Example

```
--- QUEUE STATISTICS ---
Critical (Level 1):  2 patients
Urgent (Level 2):    5 patients
Standard (Level 3):  8 patients
----
Total waiting:      15 patients
```

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **Data Structure**: Min-Heap (heapq)
- **Dependencies**: None (stdlib only)
- **Code Quality**: 13 unit tests, full error handling

## 📚 Learn More

- **For architecture details**: Read `DESIGN.md`
- **For full usage guide**: Read `README.md`
- **For code**: Read `triage_queue.py` and `cli.py`
- **For test examples**: Read `test_triage_queue.py`

## ✅ Verification Checklist

After running the system:

- [ ] CLI menu displays clearly
- [ ] Can add patients with different triage levels
- [ ] Next patient called is always highest priority
- [ ] Patients at same level are called in arrival order
- [ ] Empty queue error is handled gracefully
- [ ] Statistics show correct counts
- [ ] All tests pass (run `python test_triage_queue.py`)
- [ ] Demo runs without errors (run `python demo.py`)

## 🎓 Learning Outcomes

After studying this codebase, you'll understand:

1. **Priority Queues**: Why they're better than sorting lists
2. **Data Structures**: Heap vs array vs linked lists
3. **Algorithm Complexity**: O(log n) vs O(n) operations
4. **System Design**: Handling concurrency and edge cases
5. **Testing**: Unit tests and integration tests
6. **Production Code**: Clean, documented, error-handled code

## 🚀 Next Steps (Future Enhancements)

- Add database storage (SQLite/PostgreSQL)
- Build REST API (Flask/FastAPI)
- Add web dashboard
- Implement multi-worker threading
- Add persistence and recovery
- Track metrics and analytics

---

**Ready to explore?** Start with:
```bash
python demo.py
```

Then try:
```bash
python cli.py
```

Then read:
```
DESIGN.md
```
