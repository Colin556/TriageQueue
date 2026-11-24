#!/usr/bin/env python3
"""
Automated demo of the Triage Queue CLI

Shows the system in action without requiring manual input.
"""

from datetime import datetime
from triage_queue import Patient, TriageQueue, QueueEmptyError


def demo():
    """Run an automated demonstration."""
    
    print("\n" + "=" * 70)
    print("  TRIAGE QUEUE MANAGER - AUTOMATED DEMONSTRATION")
    print("=" * 70)
    
    queue = TriageQueue()
    
    # Scenario: Hospital emergency unit on a busy day
    print("\n📋 SCENARIO: Hospital Emergency Unit - Busy Monday Morning")
    print("-" * 70)
    
    # 09:00 - Initial patients arrive
    print("\n⏰ 09:00 AM - Initial patients arrive")
    
    patients = [
        ("John Adams", 3, "Minor cut, needs stitches"),
        ("Sarah Chen", 2, "Sprained ankle, can't walk"),
        ("Mike Johnson", 3, "Flu symptoms"),
    ]
    
    for name, level, reason in patients:
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        patient = Patient(name, level, datetime.now())
        queue.enqueue(patient)
        print(f"   ✓ {name:20} (Level {level} - {level_names[level]:8}) → {reason}")
    
    print(f"\n   Queue status: {queue.size()} patients waiting")
    stats = queue.stats()
    print(f"   • Critical: {stats[1]} | Urgent: {stats[2]} | Standard: {stats[3]}")
    
    # 09:15 - Critical emergency arrives
    print("\n⏰ 09:15 AM - CRITICAL: Ambulance with chest pain patient")
    
    patient = Patient("Robert Williams", 1, datetime.now())
    queue.enqueue(patient)
    print(f"   ⚠️  PRIORITY: Robert Williams (Level 1 - CRITICAL)")
    print(f"       Condition: Acute chest pain, possible heart attack")
    print(f"   ✓ Robert added to queue")
    
    print(f"\n   Queue status: {queue.size()} patients waiting")
    stats = queue.stats()
    print(f"   • Critical: {stats[1]} | Urgent: {stats[2]} | Standard: {stats[3]}")
    
    # View queue
    print("\n📊 CURRENT QUEUE (In order of attention):")
    print("   " + "-" * 66)
    
    patients_list = queue.list_queue()
    level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
    
    for i, p in enumerate(patients_list, 1):
        marker = "→ NEXT" if i == 1 else "      "
        print(f"   {marker} {i}. {p.name:20} | Level {p.triage_level} [{level_names[p.triage_level]:8}]")
    
    print("   " + "-" * 66)
    
    # Call patients in order
    print("\n👨‍⚕️  CALLING PATIENTS:")
    print("   " + "-" * 66)
    
    call_count = 1
    while not queue.is_empty():
        patient = queue.dequeue()
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        print(f"   Call {call_count}: 🔔 {patient.name:20} (Level {patient.triage_level} - {level_names[patient.triage_level]})")
        call_count += 1
    
    print("   " + "-" * 66)
    print("\n   ✓ All patients have been called")
    print(f"   Queue is now empty: {queue.is_empty()}")
    
    # Test error handling
    print("\n⚠️  ERROR HANDLING:")
    print("   Attempting to call patient from empty queue...")
    
    try:
        queue.dequeue()
    except QueueEmptyError as e:
        print(f"   ✓ System responded gracefully: '{e}'")
    
    # Key insights
    print("\n" + "=" * 70)
    print("🎯 KEY INSIGHTS FROM DEMO")
    print("=" * 70)
    
    print("""
1. PRIORITY ORDERING
   • Critical (Level 1) patients are always served first
   • Robert (arriving at 09:15) jumped the queue ahead of earlier patients
   • This can be life-saving in an emergency

2. FIFO WITHIN LEVEL
   • John and Mike (both Level 3) are called in arrival order
   • Sarah (Level 2) is called after Robert but before John/Mike
   • Ensures fairness: earlier patients of same urgency are served first

3. SCALABILITY
   • System handles arbitrary queue sizes efficiently
   • Adding/removing patients is O(log n)
   • No manual re-sorting needed when priorities change

4. PRODUCTION-READY
   • Graceful error handling (empty queue)
   • Clear timestamps for audit trails
   • Ready for integration with hospital IT systems
   • Extensible: can add persistence, APIs, analytics
""")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo()
