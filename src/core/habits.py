"""Habit tracking configuration and utilities."""

from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass
class Habit:
    """Definition of a trackable habit."""
    id: str
    name: str
    description: str
    
    def __hash__(self):
        return hash(self.id)


class HabitTracker:
    """Pre-configured habits for the personal agent."""
    
    # Define your habits here - change as needed
    HABITS: List[Habit] = [
        Habit(
            id="workout",
            name="45 min workout",
            description="45 min workout (or minimum 20 min)"
        ),
        Habit(
            id="walk_after_meals",
            name="10 min walk after meals",
            description="10 min walk after meals"
        ),
        Habit(
            id="eat_clean",
            name="Eat clean",
            description="Eat clean; no junk"
        ),
        Habit(
            id="sleep_timing",
            name="Sleep timing",
            description="Last food ≥4 hrs before bed"
        ),
        Habit(
            id="reading",
            name="30 min reading",
            description="30 min reading"
        ),
    ]
    
    @classmethod
    def get_all_habits(cls) -> List[Habit]:
        """Get all configured habits."""
        return cls.HABITS
    
    @classmethod
    def get_habit(cls, habit_id: str) -> Habit:
        """Get a specific habit by ID."""
        for habit in cls.HABITS:
            if habit.id == habit_id:
                return habit
        raise ValueError(f"Habit not found: {habit_id}")
    
    @classmethod
    def get_habit_ids(cls) -> List[str]:
        """Get all habit IDs."""
        return [h.id for h in cls.HABITS]
    
    @classmethod
    def list_habits(cls) -> str:
        """Get formatted list of all habits for display."""
        lines = []
        for i, habit in enumerate(cls.HABITS, 1):
            lines.append(f"  {i}. {habit.name} - {habit.description}")
        return "\n".join(lines)
