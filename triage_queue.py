"""
Triage Queue Manager

A priority queue system for hospital emergency unit patient intake.
Manages patients by triage level (1=critical, 2=urgent, 3=standard) with FIFO ordering within levels.
"""

import heapq
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict


class QueueEmptyError(Exception):
    """Raised when attempting to dequeue or peek from an empty queue."""
    pass


@dataclass
class Patient:
    """Represents a patient in the triage queue.
    
    Attributes:
        name: Patient's name
        triage_level: Priority level (1=critical, 2=urgent, 3=standard)
        arrived_at: Timestamp when patient arrived
    """
    name: str
    triage_level: int
    arrived_at: datetime

    def __post_init__(self):
        """Validate triage level is in valid range."""
        if not 1 <= self.triage_level <= 3:
            raise ValueError(f"Triage level must be 1-3, got {self.triage_level}")

    def __repr__(self) -> str:
        """Human-readable string representation."""
        level_names = {1: "CRITICAL", 2: "URGENT", 3: "STANDARD"}
        return (
            f"Patient(name={self.name!r}, level={self.triage_level} [{level_names[self.triage_level]}], "
            f"arrived_at={self.arrived_at.strftime('%H:%M:%S')})"
        )


class TriageQueue:
    """Priority queue for patient triage with arrival-time ordering within triage levels.
    
    Uses a min-heap with (triage_level, sequence_counter, patient) tuples.
    - triage_level: Lower values (critical=1) have higher priority
    - sequence_counter: Ensures FIFO for patients at the same triage level
    - patient: The actual Patient object
    
    Complexity:
    - enqueue: O(log n)
    - dequeue: O(log n)
    - peek: O(1)
    - list_queue: O(n)
    - stats: O(n)
    """

    def __init__(self):
        """Initialize an empty triage queue."""
        self._heap: List[tuple] = []  # List of (triage_level, sequence_counter, patient) tuples
        self._counter: int = 0  # Global counter for arrival order across all levels

    def enqueue(self, patient: Patient) -> None:
        """Add a patient to the queue in the correct priority position.
        
        The patient is placed according to:
        1. Triage level (1 before 2 before 3)
        2. Arrival order (FIFO) within same level
        
        Args:
            patient: Patient object to enqueue
        """
        self._counter += 1
        # Tuple comparison is lexicographic: (level, sequence, patient)
        heapq.heappush(self._heap, (patient.triage_level, self._counter, patient))

    def dequeue(self) -> Patient:
        """Remove and return the highest-priority patient.
        
        Returns:
            Patient object for the next patient to be attended
            
        Raises:
            QueueEmptyError: If the queue is empty
        """
        if not self._heap:
            raise QueueEmptyError("Cannot dequeue: queue is empty")
        
        _, _, patient = heapq.heappop(self._heap)
        return patient

    def peek(self) -> Patient:
        """Return the highest-priority patient without removing them.
        
        Returns:
            Patient object for the next patient to be attended
            
        Raises:
            QueueEmptyError: If the queue is empty
        """
        if not self._heap:
            raise QueueEmptyError("Cannot peek: queue is empty")
        
        _, _, patient = self._heap[0]
        return patient

    def list_queue(self) -> List[Patient]:
        """Return all waiting patients in the order they will be attended.
        
        Returns a copy to avoid external mutation of internal state.
        
        Returns:
            List of Patient objects in priority/arrival order
        """
        # Extract patients from heap tuples, preserving heap order
        # Note: heap structure guarantees correct priority order, not full sort
        return [patient for _, _, patient in sorted(self._heap)]

    def stats(self) -> Dict[int, int]:
        """Return count of waiting patients per triage level.
        
        Returns:
            Dictionary mapping triage level (1, 2, 3) to patient count
        """
        stats = {1: 0, 2: 0, 3: 0}
        for triage_level, _, _ in self._heap:
            stats[triage_level] += 1
        return stats

    def is_empty(self) -> bool:
        """Check if the queue is empty.
        
        Returns:
            True if no patients are waiting, False otherwise
        """
        return len(self._heap) == 0

    def size(self) -> int:
        """Return the number of patients currently in the queue.
        
        Returns:
            Total count of waiting patients
        """
        return len(self._heap)
