# PawPal+ (Module 2 Project)

This is **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Functionality

The final app allows the following:

- Lets a user enter basic owner + pet info
- Lets a user add/edit tasks (duration + priority at minimum)
- Generates a daily schedule/plan based on constraints and priorities
- Displays the plan clearly (and ideally explain the reasoning)


## Demo
<a href="/course_images/ai110/demo_screenshot.png" target="_blank"><img src='/course_images/ai110/demo_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.


## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## Features

PawPal+ currently includes the following scheduling and planning features:

- Priority-first scheduling using deterministic multi-key sorting:
	- Sort order is: priority (ascending, where 1 is highest), then preferred start time (`HH:MM`), then shorter duration, then task name.
- Due-date and status gating before scheduling:
	- Only tasks that are `pending` and due today (or overdue) are considered for the daily plan.
- Time-budget aware planning:
	- Tasks are added greedily while remaining owner time is available (`available_time_per_day`).
- Constraint-based schedule optimization:
	- Optional filtering supports `include/exclude` categories, max priority, status filters, and pet-specific filters.
- Conflict detection with slot indexing:
	- Tasks with explicit start times are tracked by `(due_date, start_time)` to detect collisions quickly and emit warnings.
- Recurring task lifecycle support:
	- Completing a daily/weekly task auto-generates the next pending instance with the correct next due date.
	- Duplicate recurring instances are prevented.
- Human-readable schedule reasoning:
	- Each scheduled task includes an explanation string, and warning messages are collected for skipped/conflicting tasks.

## Testing PawPal+

### Setup

```bash
python -m pytest
```

The tests in the PawPal+ test suite cover the following behaviors:
- Task count increase
- Marking a task complete
- Chronological order of display
- Task daily reoccurrence
- Time conflicts for tasks

Confidence level: 4.5 stars
