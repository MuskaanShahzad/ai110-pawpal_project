from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    description: str
    due_date: str
    pet_name: str
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def mark_incomplete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def view_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str, email: str) -> None:
        self.name: str = name
        self.email: str = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def view_pets(self) -> List[Pet]:
        pass


class Scheduler:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def get_today_tasks(self) -> List[Task]:
        pass

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        pass
