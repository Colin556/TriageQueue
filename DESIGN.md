# Triage Queue Manager — Design Document

## Problem Statement
A hospital emergency unit needs a priority queue system that:
- Prioritizes patients by triage level (1 = critical, 2 = urgent, 3 = standard)
- Maintains FIFO order within the same triage level
- Supports efficient enqueue, dequeue, peek, and listing operations
- Handles concurrent or near-concurrent operations gracefully

## Data Structure Choice: Min-Heap with Tie-Breaking Counter

### Why a Heap?

We use Python's `heapq` module to implement a min-heap with tuples as sort keys:

```python
(triage_level, sequence_counter, patient_object)
```

**Why heap over alternatives:**

1. **Single Deque**: Requires O(n) search + insertion on every enqueue to find the correct position → inefficient at scale.
2. **Sorted List**: Same O(n) insertion cost as deque.
3. **Three Separate Deques** (one per level): Cleaner O(1) operations but requires explicit loop during dequeue to check each queue → adds code complexity and potential for bugs.
4. **Heap**: 
   - Enqueue: O(log n) — heapq handles placement automatically
   - Dequeue: O(log n) — efficient removal from top
   - Peek: O(1) — no removal needed
   - Listing: O(n log n) or O(n) depending on method
   - Natural ordering by priority level
   - Single, well-tested data structure

### How It Works

#### Insertion (Enqueue)
When a new patient arrives:
1. Assign an incrementing `sequence_counter` (tracks arrival order globally)
2. Create tuple: `(triage_level, sequence_counter, patient)`
3. Push to heap using `heapq.heappush()`
4. Heap automatically places it in correct position: **lower triage level first, then by sequence (earlier arrivals first within same level)**

Example insertion order and heap state:
```
Insert: Patient A, level 2, seq=1 → heap = [(2, 1, PatientA)]
Insert: Patient B, level 1, seq=2 → heap = [(1, 2, PatientB), (2, 1, PatientA)]  # B jumped to front
Insert: Patient C, level 2, seq=3 → heap = [(1, 2, PatientB), (2, 1, PatientA), (2, 3, PatientC)]
Insert: Patient D, level 1, seq=4 → heap = [(1, 2, PatientB), (1, 4, PatientD), (2, 3, PatientC), (2, 1, PatientA)]
```

#### Removal (Dequeue)
1. Use `heapq.heappop()` — always removes the smallest tuple (lowest triage, earliest arrival)
2. Returns patient object
3. Heap automatically restructures

#### Peek (without removal)
1. Access `heap[0]` directly (min element in constant time)
2. Extract and return patient object without popping

### FIFO Guarantee Within Triage Level

The sequence counter ensures strict FIFO:
- Assigned at enqueue time (not peek or other operations)
- Monotonically increasing
- Python's tuple comparison is lexicographic: compares first element, then second if tied, then third
- Patients at the same level are ordered by sequence, ensuring arrival order

## Concurrency & State Mutation

### The Race Condition
In a real system with multiple workers:

```
Time T1: Worker A calls dequeue() on level-2 patient
Time T2: Worker B enqueues new level-1 patient (critical)
Time T3: Worker A removes level-2 patient from queue
```

Question: **Could the level-1 patient be served before the level-2 patient starts?**

**Answer: Yes, because dequeue happens atomically before enqueue.**

However, in a **multi-threaded** environment (not our scope here, but noted for production use):

### Preventing Double-Processing

**Strategy: Atomic State Transitions**

If we were to add threading later, the solution is:
1. **Dequeue atomically**: Remove patient from queue AND mark as "in-progress" in a single lock-protected transaction
2. **Queue state invariant**: A patient in the queue is not in an "in-progress" or "completed" state
3. **Worker responsibility**: Only workers with explicit "in-progress" claim can process and mark complete

```python
# Pseudo-code for thread-safe variant (not implemented in CLI, but good to know)
with queue_lock:
    patient = heap.pop()
    patient.state = "IN_PROGRESS"
    return patient

# Later, worker marks complete:
with queue_lock:
    patient.state = "COMPLETED"
```

**For this single-threaded CLI version:**
- No locks needed
- State mutations happen in order
- Design is naturally race-condition-free

## Implementation Structure

### Classes

#### `Patient` (dataclass)
- `name: str`
- `triage_level: int` (1-3)
- `arrived_at: datetime`
- Includes __repr__ for clean display

#### `TriageQueue`
- **Private state**: `self._heap` (list of tuples), `self._counter` (sequence counter)
- **Methods**:
  - `enqueue(patient)`: O(log n)
  - `dequeue()`: O(log n), raises exception if empty
  - `peek()`: O(1), raises exception if empty
  - `list_queue()`: O(n), returns copy of all patients in priority order
  - `stats()`: O(n), counts per level

## Edge Cases Handled

1. **Empty queue dequeue/peek**: Raise `QueueEmptyError` with descriptive message
2. **Invalid triage level**: Dataclass validation at construction time
3. **Concurrent arrival**: Sequence counter ensures deterministic ordering
4. **Large queue**: Heap operations scale gracefully (O(log n))

## Testing Recommendations (Optional)

```python
def test_level_1_preempts_level_2():
    q = TriageQueue()
    q.enqueue(Patient("Alice", 2, ...))
    q.enqueue(Patient("Bob", 1, ...))
    assert q.peek().name == "Bob"  # Level 1 comes first

def test_fifo_within_level():
    q = TriageQueue()
    q.enqueue(Patient("Alice", 2, ...))
    q.enqueue(Patient("Bob", 2, ...))
    assert q.dequeue().name == "Alice"
    assert q.dequeue().name == "Bob"
```

---

**Conclusion**: The heap-based design is efficient, scalable, and simple enough for a CLI but sophisticated enough to reflect real production patterns. The sequence counter elegantly solves the FIFO-within-level requirement without manual sorting or multiple data structures.
