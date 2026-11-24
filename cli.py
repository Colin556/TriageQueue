"""
Triage Queue CLI

Command-line interface for the hospital emergency unit triage queue manager.
Provides a simple menu-driven interface for queue operations.
"""

from datetime import datetime
from triage_queue import Patient, TriageQueue, QueueEmptyError


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("  HOSPITAL EMERGENCY UNIT - TRIAGE QUEUE MANAGER")
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\n--- MENU ---")
    print("1) Add a new patient")
    print("2) Call next patient")
    print("3) View current queue")
    print("4) See queue statistics")
    print("5) Exit")
    print("-" * 60)


def add_patient(queue: TriageQueue) -> None:
    """Prompt user to add a new patient to the queue.
    
    Args:
        queue: The TriageQueue instance
    """
    print("\n--- ADD NEW PATIENT ---")
    name = input("Patient name: ").strip()
    
    if not name:
        print("Error: Name cannot be empty")
        return
    
    # Prompt for and validate triage level
    while True:
        try:
            level_input = input("Triage level (1=Critical, 2=Urgent, 3=Standard): ").strip()
            level = int(level_input)
            if level not in [1, 2, 3]:
                print("Error: Triage level must be 1, 2, or 3")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number (1, 2, or 3)")
    
    # Create patient with current timestamp
    patient = Patient(name=name, triage_level=level, arrived_at=datetime.now())
    queue.enqueue(patient)
    
    level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
    print(f"✓ {name} added with triage level {level} [{level_names[level]}]")


def call_next_patient(queue: TriageQueue) -> None:
    """Call the next patient from the queue.
    
    Args:
        queue: The TriageQueue instance
    """
    print("\n--- CALL NEXT PATIENT ---")
    try:
        patient = queue.dequeue()
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        print(f"🔔 Calling: {patient.name} (Level {patient.triage_level} [{level_names[patient.triage_level]}])")
        print(f"   Arrived at: {patient.arrived_at.strftime('%H:%M:%S')}")
    except QueueEmptyError as e:
        print(f"⚠ {e}")


def view_queue(queue: TriageQueue) -> None:
    """Display all patients currently in the queue in order of attention.
    
    Args:
        queue: The TriageQueue instance
    """
    print("\n--- CURRENT QUEUE ---")
    
    if queue.is_empty():
        print("Queue is empty")
        return
    
    # Peek to show next patient without removing
    try:
        next_patient = queue.peek()
        print(f"Next patient: {next_patient.name} (Level {next_patient.triage_level})")
        print(f"Arrived at: {next_patient.arrived_at.strftime('%H:%M:%S')}\n")
    except QueueEmptyError:
        pass
    
    # List all patients in order
    print("All patients in queue (in order of attention):")
    print("-" * 60)
    
    patients = queue.list_queue()
    level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
    
    for i, patient in enumerate(patients, 1):
        status = "→ NEXT" if i == 1 else "  "
        print(f"{status} {i}. {patient.name:20} | Level {patient.triage_level} [{level_names[patient.triage_level]:8}] | {patient.arrived_at.strftime('%H:%M:%S')}")
    
    print("-" * 60)
    print(f"Total patients waiting: {queue.size()}")


def show_stats(queue: TriageQueue) -> None:
    """Display queue statistics.
    
    Args:
        queue: The TriageQueue instance
    """
    print("\n--- QUEUE STATISTICS ---")
    
    stats = queue.stats()
    total = queue.size()
    
    print(f"Critical (Level 1):  {stats[1]} patient{'s' if stats[1] != 1 else ''}")
    print(f"Urgent (Level 2):    {stats[2]} patient{'s' if stats[2] != 1 else ''}")
    print(f"Standard (Level 3):  {stats[3]} patient{'s' if stats[3] != 1 else ''}")
    print("-" * 60)
    print(f"Total waiting:       {total} patient{'s' if total != 1 else ''}")


def main():
    """Main CLI loop."""
    queue = TriageQueue()
    
    print_header()
    print("Welcome to the Triage Queue Manager")
    print("Type your choice (1-5) and press Enter\n")
    
    while True:
        print_menu()
        choice = input("Your choice: ").strip()
        
        if choice == "1":
            add_patient(queue)
        elif choice == "2":
            call_next_patient(queue)
        elif choice == "3":
            view_queue(queue)
        elif choice == "4":
            show_stats(queue)
        elif choice == "5":
            print("\n👋 Thank you for using Triage Queue Manager. Goodbye!\n")
            break
        else:
            print("⚠ Invalid choice. Please enter 1-5")


if __name__ == "__main__":
    main()
