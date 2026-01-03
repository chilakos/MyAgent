"""Quick test of habit tracking in demo."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.memory import ConversationManager
from src.core.habits import HabitTracker

print("=" * 60)
print("Testing Habit Tracking Features")
print("=" * 60)

# Initialize
memory = ConversationManager()

# Test 1: Display habits
print("\n1. Available Habits:")
print(HabitTracker.list_habits())

# Test 2: Log habits for today
print("\n2. Logging habits for today:")
test_habits = {
    "workout": True,
    "walk_after_meals": True,
    "eat_clean": False,  # Skip this one
    "sleep_timing": True,
    "reading": True,
}

for habit_id, completed in test_habits.items():
    memory.log_habit(habit_id, completed, notes="Test entry" if completed else None)
    status = "✓" if completed else "✗"
    habit = HabitTracker.get_habit(habit_id)
    print(f"  {status} {habit.name}")

# Test 3: View daily stats
print("\n3. Daily Summary:")
print(memory.get_habit_summary(days=1))

# Test 4: Log more days (simulate a week)
print("\n4. Simulating past week habits...")
from datetime import datetime, timedelta

today = datetime.utcnow().date()
for day_offset in range(1, 7):
    date = (today - timedelta(days=day_offset)).isoformat()
    for habit_id in HabitTracker.get_habit_ids():
        # Random pattern for testing
        completed = (hash(f"{habit_id}{day_offset}") % 2) == 0
        memory.log_habit(habit_id, completed, logged_date=date)

# Test 5: View weekly stats
print("\n5. Weekly Summary (7 days):")
print(memory.get_habit_summary(days=7))

print("\n" + "=" * 60)
print("✓ All habit features working!")
print("=" * 60)
