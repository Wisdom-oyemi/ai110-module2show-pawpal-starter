from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: float
    health_conditions: list[str] = field(default_factory=list)
    tasks: list["Task"] = field(default_factory=list)  # back-reference to assigned tasks

    def get_assigned_tasks(self) -> list:
        """Return a copy of tasks currently assigned to this pet."""
        return list(self.tasks)

    def get_special_needs(self) -> list[str]:
        """Return a copy of this pet's health-related special needs."""
        return list(self.health_conditions)


@dataclass
class Task:
    name: str
    category: str
    duration: float          # in minutes
    priority: int            # 1 (highest) to 5 (lowest)
    pet: Pet = None
    start_time: str | None = None  # optional HH:MM (24h) preferred time
    recurrence: str = "daily"  # e.g. "daily", "weekly", "as needed"
    status: str = "pending"
    due_date: date = field(default_factory=date.today)

    def get_priority(self) -> int:
        """Return this task's priority as an integer."""
        return int(self.priority)

    def is_time_available(self, time: float) -> bool:
        """Return whether the provided available time can fit this task."""
        return time >= self.duration

    def get_estimated_duration(self) -> float:
        """Return the estimated task duration in minutes."""
        return float(self.duration)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def get_next_due_date(self, from_date: date | None = None) -> date | None:
        """Return the next due date for recurring tasks."""
        recurrence = self.recurrence.strip().lower()
        anchor = from_date or self.due_date or date.today()

        if recurrence == "daily":
            return anchor + timedelta(days=1)
        if recurrence == "weekly":
            return anchor + timedelta(days=7)
        return None


class Owner:
    def __init__(self, name: str, email: str, available_time_per_day: float, preferences: dict = None):
        self.name = name
        self.email = email
        self.available_time_per_day = available_time_per_day  # in minutes
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []
        self.scheduler: "Scheduler" = None  # set after Scheduler is created

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner if it is valid and not already tracked."""
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet instance")

        if pet not in self.pets:
            self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task to this owner and sync it to the assigned pet."""
        # should also call task.pet.tasks.append(task) to keep Pet in sync
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance")

        if task.pet is not None and task.pet not in self.pets:
            self.add_pet(task.pet)

        if task not in self.tasks:
            self.tasks.append(task)

        if task.pet is not None and task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def get_schedule(self) -> list:
        """Generate and return today's schedule through the scheduler."""
        # delegates to self.scheduler.generate_schedule()
        if self.scheduler is None:
            self.scheduler = Scheduler(self)
        return self.scheduler.generate_schedule()


class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler bound to an owner and their tasks."""
        self.owner = owner
        # pets and tasks are read from owner directly — no duplicate state
        self.daily_schedule: list = []
        self.warnings: list[str] = []

    def generate_schedule(self) -> list:
        """Build a daily schedule from owner tasks using priority and time limits."""
        self.warnings = []
        today = date.today()
        available_time = float(self.owner.available_time_per_day)
        remaining_time = available_time
        start_minute = 0.0

        prioritized_tasks = sorted(
            [task for task in self.owner.tasks if self._is_due_and_pending(task, today)],
            key=lambda t: self._task_sort_key(t),
        )

        schedule: list[dict] = []
        occupied_slots: dict[tuple[date, str], Task] = {}
        for task in prioritized_tasks:
            conflict_warning = self._check_task_conflict(task, occupied_slots)
            if conflict_warning:
                self.warnings.append(conflict_warning)
                continue

            if not self.can_fit_task(task, remaining_time):
                continue

            duration = task.get_estimated_duration()
            schedule.append(
                {
                    "task": task.name,
                    "pet": task.pet.name if task.pet else None,
                    "category": task.category,
                    "priority": task.get_priority(),
                    "duration": duration,
                    "start_minute": start_minute,
                    "end_minute": start_minute + duration,
                    "recurrence": task.recurrence,
                    "reason": "Selected due to priority and available time.",
                }
            )
            start_minute += duration
            remaining_time -= duration
            self._mark_slot_occupied(task, occupied_slots)

        self.daily_schedule = schedule
        return list(self.daily_schedule)

    def optimize_schedule(self, constraints: dict) -> list:
        """Build a schedule after filtering tasks with provided constraints."""
        constraints = constraints or {}
        self.warnings = []
        today = date.today()
        max_time = float(constraints.get("max_time", self.owner.available_time_per_day))
        include_categories = constraints.get("include_categories")
        exclude_categories = set(constraints.get("exclude_categories", []))
        max_priority = constraints.get("max_priority")
        status = constraints.get("status")
        include_statuses = constraints.get("include_statuses")
        exclude_statuses = constraints.get("exclude_statuses", [])
        pet_name = constraints.get("pet_name")
        include_pets = constraints.get("include_pets")

        include_categories_set = set(include_categories) if include_categories else None
        include_statuses_set = {value.lower() for value in include_statuses} if include_statuses else None
        exclude_statuses_set = {value.lower() for value in exclude_statuses}
        include_pets_set = {name.lower() for name in include_pets} if include_pets else None
        single_pet_name = pet_name.lower() if isinstance(pet_name, str) else None
        single_status = status.lower() if isinstance(status, str) else None

        filtered_tasks = []
        for task in self.owner.tasks:
            if not self._is_due_and_pending(task, today):
                continue

            if include_categories_set and task.category not in include_categories_set:
                continue
            if task.category in exclude_categories:
                continue
            if max_priority is not None and task.get_priority() > int(max_priority):
                continue

            task_status = task.status.lower()
            task_pet_name = task.pet.name.lower() if task.pet else None

            if single_status and task_status != single_status:
                continue
            if include_statuses_set and task_status not in include_statuses_set:
                continue
            if task_status in exclude_statuses_set:
                continue

            if single_pet_name and task_pet_name != single_pet_name:
                continue
            if include_pets_set and task_pet_name not in include_pets_set:
                continue

            filtered_tasks.append(task)

        filtered_tasks.sort(key=lambda t: self._task_sort_key(t))

        schedule: list[dict] = []
        occupied_slots: dict[tuple[date, str], Task] = {}
        remaining_time = max_time
        start_minute = 0.0
        for task in filtered_tasks:
            conflict_warning = self._check_task_conflict(task, occupied_slots)
            if conflict_warning:
                self.warnings.append(conflict_warning)
                continue

            if not self.can_fit_task(task, remaining_time):
                continue

            duration = task.get_estimated_duration()
            schedule.append(
                {
                    "task": task.name,
                    "pet": task.pet.name if task.pet else None,
                    "category": task.category,
                    "priority": task.get_priority(),
                    "duration": duration,
                    "start_minute": start_minute,
                    "end_minute": start_minute + duration,
                    "recurrence": task.recurrence,
                    "reason": "Included after applying optimization constraints.",
                }
            )
            start_minute += duration
            remaining_time -= duration
            self._mark_slot_occupied(task, occupied_slots)

        self.daily_schedule = schedule
        return list(self.daily_schedule)

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of scheduled task choices."""
        if not self.daily_schedule:
            if self.warnings:
                warning_lines = "\n".join(f"- WARNING: {warning}" for warning in self.warnings)
                return "No tasks are currently scheduled.\n" + warning_lines
            return "No tasks are currently scheduled."

        lines = ["PawPal+ Schedule Reasoning:"]
        for item in self.daily_schedule:
            pet_label = f" for {item['pet']}" if item["pet"] else ""
            lines.append(
                (
                    f"- {item['task']}{pet_label}: priority {item['priority']}, "
                    f"{item['duration']} min, {item['reason']}"
                )
            )

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"- {warning}")

        return "\n".join(lines)

    def can_fit_task(self, task: Task, time: float) -> bool:
        """Return whether a task can fit within the remaining time."""
        return task.is_time_available(time)

    @staticmethod
    def _is_due_and_pending(task: Task, reference_date: date) -> bool:
        """Return whether a task should be considered for scheduling.

        A task is eligible only when it is still pending and its due date is
        today or earlier than the provided reference date.
        """
        return task.status.lower() == "pending" and task.due_date <= reference_date

    def mark_task_complete(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Complete a task and optionally create the next recurring instance.

        Behavior:
        - Marks the provided task as completed.
        - For daily/weekly recurrence, creates a new pending task with the next due date.
        - Returns the created follow-up task, or None when no follow-up is needed.
        - Adds warning messages for non-fatal issues (untracked task or duplicate recurrence).
        """
        self.warnings = []
        if task not in self.owner.tasks:
            self.warnings.append("Task completion skipped: task is not tracked by this owner.")
            return None

        if task.status.lower() == "completed":
            return None

        completion_date = completed_on or date.today()
        task.mark_complete()

        next_due_date = task.get_next_due_date(from_date=completion_date)
        if next_due_date is None:
            return None

        duplicate_exists = any(
            existing is not task
            and existing.name == task.name
            and existing.pet == task.pet
            and existing.recurrence.strip().lower() == task.recurrence.strip().lower()
            and existing.status.lower() == "pending"
            and existing.due_date == next_due_date
        for existing in self.owner.tasks)

        if duplicate_exists:
            self.warnings.append(
                f"Recurring instance already exists for '{task.name}' on {next_due_date.isoformat()}."
            )
            return None

        next_task = Task(
            name=task.name,
            category=task.category,
            duration=task.duration,
            priority=task.priority,
            pet=task.pet,
            start_time=task.start_time,
            recurrence=task.recurrence,
            status="pending",
            due_date=next_due_date,
        )
        self.owner.add_task(next_task)
        return next_task

    def get_warnings(self) -> list[str]:
        """Return the current warning messages from the latest scheduler action.

        Warnings are generated during schedule building and task completion
        checks when recoverable conflicts are detected.
        """
        return list(self.warnings)

    def _check_task_conflict(self, task: Task, occupied_slots: dict[tuple[date, str], Task]) -> str | None:
        """Validate lightweight scheduling conflicts for a single task.

        Checks duration/priority bounds, validates HH:MM format for explicit
        start times, and detects same-slot collisions using an O(1) occupied
        slot lookup keyed by (due_date, start_time).

        Returns a warning message when a conflict is found, otherwise None.
        """
        duration = task.get_estimated_duration()
        if duration <= 0:
            return f"Skipped '{task.name}': duration must be greater than 0."

        priority = task.get_priority()
        if priority < 1 or priority > 5:
            return f"Skipped '{task.name}': priority must be between 1 and 5."

        if not task.start_time:
            return None

        if self._parse_hhmm(task.start_time) > 24 * 60:
            return f"Skipped '{task.name}': start_time must be in HH:MM 24-hour format."

        slot_key = (task.due_date, task.start_time)
        existing = occupied_slots.get(slot_key)
        if not existing:
            return None

        if task.pet and existing.pet:
            return (
                f"Skipped '{task.name}': conflicts with '{existing.name}' at "
                f"{task.start_time} on {task.due_date.isoformat()} "
                f"({task.pet.name} vs {existing.pet.name})."
            )
        return (
            f"Skipped '{task.name}': conflicts with '{existing.name}' at "
            f"{task.start_time} on {task.due_date.isoformat()}."
        )

    @staticmethod
    def _mark_slot_occupied(task: Task, occupied_slots: dict[tuple[date, str], Task]) -> None:
        """Register a task's explicit start-time slot for future collision checks.

        Only tasks with an explicit start time are added to the occupied-slot
        index because untimed tasks are sequenced by duration in the schedule.
        """
        if task.start_time:
            occupied_slots[(task.due_date, task.start_time)] = task

    @staticmethod
    def _parse_hhmm(value: str | None) -> int:
        """Convert HH:MM text to minutes from midnight.

        Returns a sentinel value larger than a full day for missing/invalid
        inputs so those values naturally sort after valid times.
        """
        if not value or not isinstance(value, str):
            return 24 * 60 + 1

        text = value.strip()
        try:
            hour_text, minute_text = text.split(":", 1)
            hour = int(hour_text)
            minute = int(minute_text)
        except (ValueError, TypeError):
            return 24 * 60 + 1

        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return 24 * 60 + 1
        return (hour * 60) + minute

    def _task_sort_key(self, task: Task) -> tuple:
        """Build the scheduler sort key for deterministic task ordering.

        Ordering precedence:
        1. Higher urgency first (lower numeric priority value).
        2. Earlier explicit HH:MM start time.
        3. Shorter estimated duration.
        4. Alphabetical task name for stable tie-breaking.
        """
        return (
            task.get_priority(),
            self._parse_hhmm(task.start_time),
            task.get_estimated_duration(),
            task.name.lower(),
        )
