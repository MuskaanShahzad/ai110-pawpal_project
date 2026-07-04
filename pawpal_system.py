from dataclasses import dataclass, replace
from datetime import date, time, datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    title: str
    description: str
    due_date: date
    pet_name: str
    completed: bool = False
    due_time: time = time(0, 0)
    duration_minutes: int = 30
    recurrence: Optional[str] = None  # "daily", "weekly", or None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not yet completed."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int

    def add_task(self, task: Task, scheduler: "Scheduler") -> None:
        """Link this task to the pet and register it with the scheduler."""
        task.pet_name = self.name
        scheduler.add_task(task)

    def view_tasks(self, scheduler: "Scheduler") -> List[Task]:
        """Return all tasks assigned to this pet from the scheduler."""
        return scheduler.get_tasks_by_pet(self.name)


class Owner:
    def __init__(self, name: str, email: str) -> None:
        self.name: str = name
        self.email: str = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self.pets.remove(pet)

    def view_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


class Scheduler:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task, printing a warning for every detected time conflict."""
        for warning in self.check_conflicts(task):
            print(f"  Warning: {warning}")
        self.tasks.append(task)

    def _conflicts(self, new_task: Task) -> List[Task]:
        """Return all tasks on the same date whose time window overlaps with new_task."""
        conflicts = []
        new_start = datetime.combine(new_task.due_date, new_task.due_time)
        new_end = new_start + timedelta(minutes=new_task.duration_minutes)
        for t in self.tasks:
            if t.due_date != new_task.due_date:
                continue
            t_start = datetime.combine(t.due_date, t.due_time)
            t_end = t_start + timedelta(minutes=t.duration_minutes)
            if new_start < t_end and new_end > t_start:
                conflicts.append(t)
        return conflicts

    def check_conflicts(self, task: Task) -> List[str]:
        """Return a list of human-readable warning strings for any time overlaps.

        Checks both same-pet and cross-pet conflicts — an owner can only be
        in one place at a time regardless of which pet is involved.
        """
        warnings = []
        for conflict in self._conflicts(task):
            if conflict.pet_name == task.pet_name:
                warnings.append(
                    f"'{task.title}' and '{conflict.title}' overlap "
                    f"for {task.pet_name}"
                )
            else:
                warnings.append(
                    f"'{task.title}' ({task.pet_name}) and "
                    f"'{conflict.title}' ({conflict.pet_name}) overlap "
                    f"— you can't do both at once"
                )
        return warnings

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks sorted chronologically by due_time.

        Uses a lambda as the sort key so Python's sorted() compares
        time objects directly — no string parsing needed.
        Does not modify the original list.
        """
        return sorted(tasks, key=lambda t: t.due_time)

    def get_today_tasks(self) -> List[Task]:
        """Return all tasks due today, sorted chronologically by time."""
        today = date.today()
        tasks = [t for t in self.tasks if t.due_date == today]
        return self.sort_by_time(tasks)

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks assigned to the given pet name."""
        return [task for task in self.tasks if task.pet_name == pet_name]

    def get_tasks_by_owner(self, owner: "Owner") -> List[Task]:
        """Return all tasks across every pet owned by this owner."""
        pet_names = {pet.name for pet in owner.pets}
        return [task for task in self.tasks if task.pet_name in pet_names]

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        on_date: Optional[date] = None,
    ) -> List[Task]:
        """Return tasks matching all provided filters in a single pass.

        Any combination of filters may be applied at once:
          - pet_name: keep only tasks for this pet (None = all pets)
          - completed: True for done tasks, False for pending (None = both)
          - on_date:   keep only tasks due on this date (None = all dates)

        Omitting a parameter leaves that dimension unfiltered.
        """
        return [
            t for t in self.tasks
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
            and (on_date is None or t.due_date == on_date)
        ]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-schedule its next occurrence.

        Uses timedelta to compute the next due date from the task's own
        due_date (not today), so late completions don't shift the schedule:
          - "daily"  → due_date + 1 day
          - "weekly" → due_date + 7 days

        Returns the newly created Task, or None if the task is not recurring
        or the next occurrence already exists in the scheduler.
        """
        task.mark_complete()
        if task.recurrence == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_date = task.due_date + timedelta(weeks=1)
        else:
            return None
        already_exists = any(
            t.title == task.title
            and t.pet_name == task.pet_name
            and t.due_date == next_date
            for t in self.tasks
        )
        if already_exists:
            return None
        next_task = Task(
            title=task.title,
            description=task.description,
            due_date=next_date,
            pet_name=task.pet_name,
            due_time=task.due_time,
            duration_minutes=task.duration_minutes,
            recurrence=task.recurrence,
        )
        self.tasks.append(next_task)
        return next_task

    def generate_recurring(self, days_ahead: int = 7) -> None:
        """Bulk-expand all recurring tasks forward by up to days_ahead days.

        For each task marked "daily" or "weekly", chains new Task copies
        using timedelta — daily adds 1 day, weekly adds 7 — until the
        deadline is reached. Skips dates that already have an occurrence
        to prevent duplicates. Uses dataclasses.replace() so all fields
        are copied automatically; only due_date and completed are overridden.
        """
        deadline = date.today() + timedelta(days=days_ahead)
        existing = {(t.title, t.pet_name, t.due_date) for t in self.tasks}
        for task in [t for t in self.tasks if t.recurrence in ("daily", "weekly")]:
            delta = timedelta(days=1) if task.recurrence == "daily" else timedelta(weeks=1)
            next_date = task.due_date + delta
            while next_date <= deadline:
                key = (task.title, task.pet_name, next_date)
                if key not in existing:
                    self.tasks.append(replace(task, due_date=next_date, completed=False))
                    existing.add(key)
                next_date += delta
