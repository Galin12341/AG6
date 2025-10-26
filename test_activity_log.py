"""
Unit tests for Activity Log application.
"""

import os
import json
import pytest
from activity_log import ActivityLog


@pytest.fixture
def temp_log(tmp_path):
    """Create a temporary activity log for testing."""
    test_file = tmp_path / "test_activities.json"
    log = ActivityLog(filename=str(test_file))
    yield log
    # Cleanup
    if test_file.exists():
        test_file.unlink()


class TestActivityLog:
    """Test suite for ActivityLog class."""

    def test_initialization(self, temp_log):
        """Test that ActivityLog initializes correctly."""
        assert temp_log.activities == []
        assert temp_log.filename.endswith("test_activities.json")

    def test_add_activity(self, temp_log):
        """Test adding a new activity."""
        activity = temp_log.add_activity("Write tests", "development")
        
        assert activity["description"] == "Write tests"
        assert activity["category"] == "development"
        assert activity["id"] == 1
        assert activity["completed"] is False
        assert "timestamp" in activity

    def test_add_multiple_activities(self, temp_log):
        """Test adding multiple activities."""
        temp_log.add_activity("Task 1", "work")
        temp_log.add_activity("Task 2", "personal")
        temp_log.add_activity("Task 3", "work")
        
        assert len(temp_log.activities) == 3
        assert temp_log.activities[0]["id"] == 1
        assert temp_log.activities[2]["id"] == 3

    def test_list_activities(self, temp_log):
        """Test listing all activities."""
        temp_log.add_activity("Task 1", "work")
        temp_log.add_activity("Task 2", "personal")
        
        activities = temp_log.list_activities()
        assert len(activities) == 2

    def test_list_activities_by_category(self, temp_log):
        """Test filtering activities by category."""
        temp_log.add_activity("Task 1", "work")
        temp_log.add_activity("Task 2", "personal")
        temp_log.add_activity("Task 3", "work")
        
        work_activities = temp_log.list_activities(category="work")
        assert len(work_activities) == 2
        assert all(a["category"] == "work" for a in work_activities)

    def test_complete_activity(self, temp_log):
        """Test marking an activity as completed."""
        activity = temp_log.add_activity("Task to complete", "test")
        activity_id = activity["id"]
        
        result = temp_log.complete_activity(activity_id)
        assert result is True
        assert temp_log.activities[0]["completed"] is True
        assert "completed_at" in temp_log.activities[0]

    def test_complete_nonexistent_activity(self, temp_log):
        """Test completing an activity that doesn't exist."""
        result = temp_log.complete_activity(999)
        assert result is False

    def test_delete_activity(self, temp_log):
        """Test deleting an activity."""
        activity = temp_log.add_activity("Task to delete", "test")
        activity_id = activity["id"]
        
        result = temp_log.delete_activity(activity_id)
        assert result is True
        assert len(temp_log.activities) == 0

    def test_delete_nonexistent_activity(self, temp_log):
        """Test deleting an activity that doesn't exist."""
        temp_log.add_activity("Task 1", "test")
        result = temp_log.delete_activity(999)
        assert result is False
        assert len(temp_log.activities) == 1

    def test_get_statistics_empty(self, temp_log):
        """Test statistics for empty log."""
        stats = temp_log.get_statistics()
        
        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["pending"] == 0
        assert stats["categories"] == {}

    def test_get_statistics(self, temp_log):
        """Test statistics calculation."""
        temp_log.add_activity("Task 1", "work")
        temp_log.add_activity("Task 2", "work")
        temp_log.add_activity("Task 3", "personal")
        temp_log.complete_activity(1)
        
        stats = temp_log.get_statistics()
        
        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 2
        assert stats["categories"]["work"] == 2
        assert stats["categories"]["personal"] == 1

    def test_persistence(self, tmp_path):
        """Test that activities persist across instances."""
        test_file = tmp_path / "persist_test.json"
        
        # Create first instance and add activity
        log1 = ActivityLog(filename=str(test_file))
        log1.add_activity("Persistent task", "test")
        
        # Create second instance and verify data loaded
        log2 = ActivityLog(filename=str(test_file))
        assert len(log2.activities) == 1
        assert log2.activities[0]["description"] == "Persistent task"
        
        # Cleanup
        test_file.unlink()

    def test_load_corrupted_file(self, tmp_path):
        """Test handling of corrupted JSON file."""
        test_file = tmp_path / "corrupted.json"
        test_file.write_text("not valid json{")
        
        log = ActivityLog(filename=str(test_file))
        assert log.activities == []
        
        # Cleanup
        test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


#