"""
Unit tests for the Triage Queue Manager

Demonstrates correctness of priority ordering and FIFO behavior within levels.
Tests all core operations and edge cases.
"""

from datetime import datetime, timedelta
from triage_queue import Patient, TriageQueue, QueueEmptyError


def test_level_priority():
    """Test that level 1 patients are always served first."""
    queue = TriageQueue()
    now = datetime.now()
    
    queue.enqueue(Patient("Alice", 2, now))
    queue.enqueue(Patient("Bob", 1, now + timedelta(seconds=1)))
    
    # Level 1 should be first even though it arrived later
    assert queue.peek().name == "Bob"
    print("✓ test_level_priority passed")


def test_fifo_within_same_level():
    """Test that FIFO ordering is maintained within the same triage level."""
    queue = TriageQueue()
    now = datetime.now()
    
    p1 = Patient("Alice", 2, now)
    p2 = Patient("Bob", 2, now + timedelta(seconds=1))
    p3 = Patient("Charlie", 2, now + timedelta(seconds=2))
    
    queue.enqueue(p1)
    queue.enqueue(p2)
    queue.enqueue(p3)
    
    # Should dequeue in arrival order
    assert queue.dequeue().name == "Alice"
    assert queue.dequeue().name == "Bob"
    assert queue.dequeue().name == "Charlie"
    print("✓ test_fifo_within_same_level passed")


def test_mixed_levels_fifo():
    """Test complex scenario: mixed levels with FIFO within levels."""
    queue = TriageQueue()
    now = datetime.now()
    
    queue.enqueue(Patient("Alice", 2, now))
    queue.enqueue(Patient("Bob", 3, now + timedelta(seconds=1)))
    queue.enqueue(Patient("Charlie", 1, now + timedelta(seconds=2)))
    queue.enqueue(Patient("Diana", 2, now + timedelta(seconds=3)))
    queue.enqueue(Patient("Eve", 1, now + timedelta(seconds=4)))
    
    # Expected order: Charlie (L1, t=2), Eve (L1, t=4), Alice (L2, t=0), Diana (L2, t=3), Bob (L3, t=1)
    assert queue.dequeue().name == "Charlie"  # Level 1, arrived first at level 1
    assert queue.dequeue().name == "Eve"       # Level 1, arrived second at level 1
    assert queue.dequeue().name == "Alice"     # Level 2, arrived first at level 2
    assert queue.dequeue().name == "Diana"     # Level 2, arrived second at level 2
    assert queue.dequeue().name == "Bob"       # Level 3
    print("✓ test_mixed_levels_fifo passed")


def test_empty_queue_dequeue():
    """Test that dequeue raises error on empty queue."""
    queue = TriageQueue()
    try:
        queue.dequeue()
        assert False, "Should raise QueueEmptyError"
    except QueueEmptyError as e:
        assert "empty" in str(e).lower()
        print("✓ test_empty_queue_dequeue passed")


def test_empty_queue_peek():
    """Test that peek raises error on empty queue."""
    queue = TriageQueue()
    try:
        queue.peek()
        assert False, "Should raise QueueEmptyError"
    except QueueEmptyError as e:
        assert "empty" in str(e).lower()
        print("✓ test_empty_queue_peek passed")


def test_peek_does_not_remove():
    """Test that peek returns patient without removing from queue."""
    queue = TriageQueue()
    now = datetime.now()
    patient = Patient("Alice", 1, now)
    
    queue.enqueue(patient)
    
    # Peek multiple times should return same patient
    assert queue.peek().name == "Alice"
    assert queue.peek().name == "Alice"
    assert queue.size() == 1
    
    # Dequeue should still work
    assert queue.dequeue().name == "Alice"
    assert queue.is_empty()
    print("✓ test_peek_does_not_remove passed")


def test_list_queue_order():
    """Test that list_queue returns patients in correct priority order."""
    queue = TriageQueue()
    now = datetime.now()
    
    queue.enqueue(Patient("Alice", 2, now))
    queue.enqueue(Patient("Bob", 1, now + timedelta(seconds=1)))
    queue.enqueue(Patient("Charlie", 3, now + timedelta(seconds=2)))
    queue.enqueue(Patient("Diana", 2, now + timedelta(seconds=3)))
    
    patients = queue.list_queue()
    
    # Should be in priority order
    assert len(patients) == 4
    assert patients[0].name == "Bob"       # Level 1
    assert patients[1].name == "Alice"     # Level 2, arrived first
    assert patients[2].name == "Diana"     # Level 2, arrived second
    assert patients[3].name == "Charlie"   # Level 3
    print("✓ test_list_queue_order passed")


def test_stats():
    """Test that stats correctly counts patients per level."""
    queue = TriageQueue()
    now = datetime.now()
    
    queue.enqueue(Patient("Alice", 1, now))
    queue.enqueue(Patient("Bob", 1, now + timedelta(seconds=1)))
    queue.enqueue(Patient("Charlie", 2, now + timedelta(seconds=2)))
    queue.enqueue(Patient("Diana", 3, now + timedelta(seconds=3)))
    
    stats = queue.stats()
    
    assert stats[1] == 2
    assert stats[2] == 1
    assert stats[3] == 1
    print("✓ test_stats passed")


def test_stats_empty_queue():
    """Test that stats returns zeros for empty queue."""
    queue = TriageQueue()
    stats = queue.stats()
    
    assert stats[1] == 0
    assert stats[2] == 0
    assert stats[3] == 0
    print("✓ test_stats_empty_queue passed")


def test_size_and_is_empty():
    """Test size() and is_empty() methods."""
    queue = TriageQueue()
    now = datetime.now()
    
    assert queue.is_empty() is True
    assert queue.size() == 0
    
    queue.enqueue(Patient("Alice", 1, now))
    assert queue.is_empty() is False
    assert queue.size() == 1
    
    queue.enqueue(Patient("Bob", 2, now + timedelta(seconds=1)))
    assert queue.size() == 2
    
    queue.dequeue()
    assert queue.size() == 1
    assert queue.is_empty() is False
    
    queue.dequeue()
    assert queue.size() == 0
    assert queue.is_empty() is True
    print("✓ test_size_and_is_empty passed")


def test_critical_patient_preemption():
    """Test that a critical patient arriving mid-queue is placed first."""
    queue = TriageQueue()
    now = datetime.now()
    
    # Add some urgent and standard patients
    queue.enqueue(Patient("Alice", 2, now))
    queue.enqueue(Patient("Bob", 2, now + timedelta(seconds=1)))
    queue.enqueue(Patient("Charlie", 3, now + timedelta(seconds=2)))
    
    # A critical patient arrives
    queue.enqueue(Patient("Dr. Emergency", 1, now + timedelta(seconds=3)))
    
    # Critical patient should be first despite arriving last
    assert queue.peek().name == "Dr. Emergency"
    
    # Dequeue order should be: Critical, then Urgent (FIFO), then Standard
    assert queue.dequeue().name == "Dr. Emergency"
    assert queue.dequeue().name == "Alice"
    assert queue.dequeue().name == "Bob"
    assert queue.dequeue().name == "Charlie"
    print("✓ test_critical_patient_preemption passed")


def test_patient_validation():
    """Test that Patient class validates triage level."""
    now = datetime.now()
    
    # Valid levels
    Patient("Alice", 1, now)
    Patient("Bob", 2, now)
    Patient("Charlie", 3, now)
    
    # Invalid levels
    try:
        Patient("Invalid", 0, now)
        assert False, "Should reject level 0"
    except ValueError:
        pass
    
    try:
        Patient("Invalid", 4, now)
        assert False, "Should reject level 4"
    except ValueError:
        pass
    
    print("✓ test_patient_validation passed")


def test_stress_large_queue():
    """Stress test with many patients."""
    queue = TriageQueue()
    now = datetime.now()
    
    # Add 1000 patients in random order
    import random
    patients = []
    for i in range(1000):
        level = random.randint(1, 3)
        patient = Patient(f"Patient_{i}", level, now + timedelta(seconds=i))
        patients.append((level, i, patient))
        queue.enqueue(patient)
    
    # Verify size
    assert queue.size() == 1000
    
    # Verify dequeue order respects priority and FIFO
    last_level = 0
    last_sequence = -1
    while not queue.is_empty():
        patient = queue.dequeue()
        # Find this patient in our original list to get its level and sequence
        level = next(p[0] for p in patients if p[2] is patient)
        seq = next(p[1] for p in patients if p[2] is patient)
        
        # Level should not decrease
        assert level >= last_level, f"Level decreased: {last_level} -> {level}"
        # If same level, sequence should increase
        if level == last_level:
            assert seq > last_sequence, f"Sequence not FIFO at level {level}: {last_sequence} -> {seq}"
        
        last_level = level
        last_sequence = seq
    
    assert queue.is_empty()
    print("✓ test_stress_large_queue passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RUNNING TRIAGE QUEUE UNIT TESTS")
    print("=" * 60 + "\n")
    
    test_level_priority()
    test_fifo_within_same_level()
    test_mixed_levels_fifo()
    test_empty_queue_dequeue()
    test_empty_queue_peek()
    test_peek_does_not_remove()
    test_list_queue_order()
    test_stats()
    test_stats_empty_queue()
    test_size_and_is_empty()
    test_critical_patient_preemption()
    test_patient_validation()
    test_stress_large_queue()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
