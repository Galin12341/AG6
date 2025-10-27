# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python utility library project containing:
- **Utility modules** (`src/`): Reusable array and string functions
- **Activity Log application** (`new.py`): A JSON-based activity tracking CLI tool
- **Test suites** (`tests/`, root-level test files): pytest-based tests for all functionality

## Running Tests

This project uses pytest for testing. Tests are located in two places:
- `tests/` directory for utility functions (test_arrays.py, test_strings.py)
- Root directory for application tests (test_activity_log.py, test_rerere.py)

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_arrays.py
pytest test_activity_log.py
```

Run a specific test function:
```bash
pytest tests/test_arrays.py::test_head
pytest test_activity_log.py::TestActivityLog::test_add_activity
```

## Code Architecture

### Utility Modules (src/)

**src/array_utils.py**: Array manipulation functions
- `head(xs)`: Returns the first element of a list

**src/strings.py**: String manipulation functions
- `shout(s)`: Converts a string to uppercase

These utilities follow a functional programming style with simple, composable functions.

### Activity Log Application (new.py)

The Activity Log is a JSON-based CLI application for tracking activities with timestamps.

**Core class**: `ActivityLog`
- Data persistence via JSON file storage (default: `activities.json`)
- Each activity has: id, description, category, timestamp, completed status
- Main operations: add, list, complete, delete activities, and view statistics

**Key methods**:
- `add_activity(description, category)`: Creates new activity
- `list_activities(category=None)`: Lists activities with optional category filter
- `complete_activity(activity_id)`: Marks activity as completed with timestamp
- `delete_activity(activity_id)`: Removes activity from log
- `get_statistics()`: Returns counts by status and category

The application uses automatic file persistence - all modifications are immediately saved to the JSON file.

### Test Structure

Tests follow pytest conventions:
- Fixture-based setup using `@pytest.fixture`
- Class-based test organization (`TestActivityLog`)
- Use of `tmp_path` fixture for file-based tests to ensure isolation
- Comprehensive coverage including edge cases (corrupted files, nonexistent IDs, persistence)

When importing from utility modules in tests, use: `from src.module_name import function_name`

## Project Context

This appears to be a homework/educational project (AG6/Homework6) focused on:
- Git workflow and branching strategies (based on git history)
- Python utility function development
- Test-driven development with pytest
- File I/O and JSON data persistence
