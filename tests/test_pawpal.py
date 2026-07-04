from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(title="Feed Biscuit") -> Task:
    return Task(title=title, description="Test task", due_date=date.today(), pet_name="")


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()
    assert task.completed is True


def test_mark_incomplete_changes_status():
    task = make_task()
    task.mark_complete()
    task.mark_incomplete()
    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    assert len(scheduler.get_tasks_by_pet("Biscuit")) == 0

    pet.add_task(make_task(), scheduler)
    assert len(scheduler.get_tasks_by_pet("Biscuit")) == 1

    pet.add_task(make_task("Walk Biscuit"), scheduler)
    assert len(scheduler.get_tasks_by_pet("Biscuit")) == 2
