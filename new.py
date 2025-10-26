"""
Activity Log Application
A simple application to track daily activities with timestamps.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional


class ActivityLog:
    """Main class for managing activity logs."""

    def __init__(self, filename: str = "activities.json"):
        """Initialize the activity log.

        Args:
            filename: Path to the JSON file for storing activities.
        """
        self.filename = filename
        self.activities: List[Dict] = []
        self.load_activities()

    def load_activities(self) -> None:
        """Load activities from JSON file."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.activities = json.load(f)
        except FileNotFoundError:
            self.activities = []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {self.filename}")
            self.activities = []

    def save_activities(self) -> None:
        """Save activities to JSON file."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.activities, f, indent=2, ensure_ascii=False)

    def add_activity(self, description: str, category: str = "general") -> Dict:
        """Add a new activity to the log.

        Args:
            description: Description of the activity.
            category: Category of the activity.

        Returns:
            The created activity dictionary.
        """
        activity = {
            "id": len(self.activities) + 1,
            "description": description,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "completed": False,
        }
        self.activities.append(activity)
        self.save_activities()
        return activity

    def list_activities(self, category: Optional[str] = None) -> List[Dict]:
        """List all activities, optionally filtered by category.

        Args:
            category: Optional category filter.

        Returns:
            List of activities.
        """
        if category:
            return [a for a in self.activities if a.get("category") == category]
        return self.activities

    def complete_activity(self, activity_id: int) -> bool:
        """Mark an activity as completed.

        Args:
            activity_id: ID of the activity to complete.

        Returns:
            True if successful, False otherwise.
        """
        for activity in self.activities:
            if activity.get("id") == activity_id:
                activity["completed"] = True
                activity["completed_at"] = datetime.now().isoformat()
                self.save_activities()
                return True
        return False

    def delete_activity(self, activity_id: int) -> bool:
        """Delete an activity from the log.

        Args:
            activity_id: ID of the activity to delete.

        Returns:
            True if successful, False otherwise.
        """
        original_length = len(self.activities)
        self.activities = [a for a in self.activities if a.get("id") != activity_id]
        if len(self.activities) < original_length:
            self.save_activities()
            return True
        return False

    def get_statistics(self) -> Dict:
        """Get statistics about activities.

        Returns:
            Dictionary with statistics.
        """
        total = len(self.activities)
        completed = sum(1 for a in self.activities if a.get("completed"))
        categories = {}

        for activity in self.activities:
            cat = activity.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "categories": categories,
        }


def main():
    """Main function for CLI interface."""
    log = ActivityLog()

    print("=== Activity Log ===")
    print("1. Add activity")
    print("2. List activities")
    print("3. Complete activity")
    print("4. Delete activity")
    print("5. Show statistics")
    print("6. Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        desc = input("Description: ")
        cat = input("Category: ")
        activity = log.add_activity(desc, cat)
        print(f"Added activity #{activity['id']}")

    elif choice == "2":
        for activity in log.list_activities():
            status = "✓" if activity.get("completed") else "○"
            print(f"{status} [{activity['id']}] {activity['description']} ({activity['category']})")

    elif choice == "5":
        stats = log.get_statistics()
        print(f"\nTotal: {stats['total']}")
        print(f"Completed: {stats['completed']}")
        print(f"Pending: {stats['pending']}")
        print(f"Categories: {stats['categories']}")


if __name__ == "__main__":
    main()
#Make a change Here for exercise 3
#make a differet at E1Test(rebaseTest's target rebase)2