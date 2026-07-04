from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class Task:
    title: str
    description: str
    due_date: date
    pet_name: str
    completed: bool = False

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
        """Add a task to the central task list."""
        self.tasks.append(task)

    def get_today_tasks(self) -> List[Task]:
        """Return all tasks whose due date is today."""
        today = date.today()
        return [task for task in self.tasks if task.due_date == today]

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks assigned to the given pet name."""
        return [task for task in self.tasks if task.pet_name == pet_name]

    def get_tasks_by_owner(self, owner: Owner) -> List[Task]:
        """Return all tasks across every pet owned by this owner."""
        pet_names = {pet.name for pet in owner.pets}
        return [task for task in self.tasks if task.pet_name in pet_names]
