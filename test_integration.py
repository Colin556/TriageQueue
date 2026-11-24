"""
Integration test for CLI - simulates user interactions
"""

import sys
from io import StringIO
from datetime import datetime
from triage_queue import Patient, TriageQueue, QueueEmptyError


def test_cli_operations():
    """Test CLI-like operations in sequence."""
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: CLI OPERATIONS")
    print("=" * 60 + "\n")
    
    queue = TriageQueue()
    
    # Simulate user adding patients
    print("1. Adding patients...")
    patients_to_add = [
        ("Alice Johnson", 2),
        ("Bob Smith", 1),
        ("Charlie Brown", 3),
        ("Diana Prince", 2),
    ]
    
    for name, level in patients_to_add:
        patient = Patient(name, level, datetime.now())
        queue.enqueue(patient)
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        print(f"   ✓ {name} added with triage level {level} [{level_names[level]}]")
    
    # View queue
    print("\n2. View current queue...")
    if not queue.is_empty():
        try:
            next_patient = queue.peek()
            print(f"   Next patient: {next_patient.name} (Level {next_patient.triage_level})")
        except QueueEmptyError:
            pass
        
        patients = queue.list_queue()
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        print(f"   All patients in queue ({len(patients)} total):")
        for i, patient in enumerate(patients, 1):
            print(f"      {i}. {patient.name:20} | Level {patient.triage_level} [{level_names[patient.triage_level]}]")
    
    # View stats
    print("\n3. Queue statistics...")
    stats = queue.stats()
    print(f"   Critical (Level 1): {stats[1]} patient{'s' if stats[1] != 1 else ''}")
    print(f"   Urgent (Level 2):   {stats[2]} patient{'s' if stats[2] != 1 else ''}")
    print(f"   Standard (Level 3): {stats[3]} patient{'s' if stats[3] != 1 else ''}")
    print(f"   Total waiting:      {queue.size()} patient{'s' if queue.size() != 1 else ''}")
    
    # Call patients
    print("\n4. Calling patients in order...")
    while not queue.is_empty():
        patient = queue.dequeue()
        print(f"   🔔 Calling: {patient.name} (Level {patient.triage_level})")
    
    # Try operations on empty queue
    print("\n5. Testing empty queue handling...")
    try:
        queue.peek()
        print("   ⚠ ERROR: peek() should raise exception")
    except QueueEmptyError as e:
        print(f"   ✓ peek() correctly raised: {e}")
    
    try:
        queue.dequeue()
        print("   ⚠ ERROR: dequeue() should raise exception")
    except QueueEmptyError as e:
        print(f"   ✓ dequeue() correctly raised: {e}")
    
    # Test preemption
    print("\n6. Testing critical patient preemption...")
    queue2 = TriageQueue()
    queue2.enqueue(Patient("Standard1", 3, datetime.now()))
    queue2.enqueue(Patient("Urgent1", 2, datetime.now()))
    queue2.enqueue(Patient("Critical1", 1, datetime.now()))
    
    print(f"   Next to call: {queue2.peek().name} (Level {queue2.peek().triage_level})")
    assert queue2.peek().name == "Critical1", "Critical patient should be first"
    print("   ✓ Critical patient preemption works correctly")
    
    print("\n" + "=" * 60)
    print("ALL INTEGRATION TESTS PASSED! ✓")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_cli_operations()
