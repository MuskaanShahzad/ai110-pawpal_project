from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(title="Feed Biscuit", due_time=time(8, 0), duration_minutes=0) -> Task:
    return Task(title=title, description="Test task", due_date=date.today(), pet_name="",
                due_time=due_time, duration_minutes=duration_minutes)


# --- Original tests ---

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


# --- Sort by time ---

def test_get_today_tasks_sorted_by_time():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(Task("Afternoon Walk", "Walk", date.today(), "", due_time=time(14, 0)), scheduler)
    pet.add_task(Task("Morning Walk",   "Walk", date.today(), "", due_time=time(7, 0)),  scheduler)
    pet.add_task(Task("Midday Feed",    "Feed", date.today(), "", due_time=time(12, 0)), scheduler)

    tasks = scheduler.get_today_tasks()
    assert tasks[0].due_time == time(7, 0)
    assert tasks[1].due_time == time(12, 0)
    assert tasks[2].due_time == time(14, 0)


def test_tomorrow_tasks_excluded_from_today():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    tomorrow = date.today() + timedelta(days=1)

    pet.add_task(Task("Walk",    "Walk", date.today(), "", due_time=time(7, 0)),  scheduler)
    pet.add_task(Task("Grooming", "Brush", tomorrow,   "", due_time=time(10, 0)), scheduler)

    assert len(scheduler.get_today_tasks()) == 1


# --- Filter by pet / status / date ---

def test_filter_by_pet():
    scheduler = Scheduler()
    pet1 = Pet(name="Biscuit",  species="Dog", age=3)
    pet2 = Pet(name="Whiskers", species="Cat", age=5)

    pet1.add_task(make_task("Walk"), scheduler)
    pet2.add_task(make_task("Feed"), scheduler)

    biscuit_tasks = scheduler.filter_tasks(pet_name="Biscuit")
    assert len(biscuit_tasks) == 1
    assert biscuit_tasks[0].title == "Walk"


def test_filter_by_completed_status():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(make_task("Walk"), scheduler)
    pet.add_task(make_task("Feed"), scheduler)
    scheduler.tasks[0].mark_complete()

    done    = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)
    assert len(done) == 1
    assert len(pending) == 1


def test_filter_combined_pet_and_status():
    scheduler = Scheduler()
    pet1 = Pet(name="Biscuit",  species="Dog", age=3)
    pet2 = Pet(name="Whiskers", species="Cat", age=5)

    pet1.add_task(make_task("Walk"), scheduler)
    pet1.add_task(make_task("Feed"), scheduler)
    pet2.add_task(make_task("Meds"), scheduler)

    scheduler.tasks[0].mark_complete()

    result = scheduler.filter_tasks(pet_name="Biscuit", completed=False)
    assert len(result) == 1
    assert result[0].title == "Feed"


def test_filter_by_date():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    tomorrow = date.today() + timedelta(days=1)

    pet.add_task(Task("Walk",     "Walk",  date.today(), "", due_time=time(7, 0)),  scheduler)
    pet.add_task(Task("Grooming", "Brush", tomorrow,     "", due_time=time(10, 0)), scheduler)

    assert len(scheduler.filter_tasks(on_date=date.today())) == 1
    assert len(scheduler.filter_tasks(on_date=tomorrow)) == 1


# --- Recurring tasks ---

def test_generate_recurring_daily_creates_future_tasks():
    scheduler = Scheduler()
    task = Task("Morning Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)
    scheduler.generate_recurring(days_ahead=2)

    dates = {t.due_date for t in scheduler.tasks if t.title == "Morning Walk"}
    assert date.today() + timedelta(days=1) in dates
    assert date.today() + timedelta(days=2) in dates


def test_generate_recurring_weekly_creates_correct_date():
    scheduler = Scheduler()
    task = Task("Bath", "Bath", date.today(), "Biscuit",
                due_time=time(10, 0), duration_minutes=30, recurrence="weekly")
    scheduler.tasks.append(task)
    scheduler.generate_recurring(days_ahead=7)

    dates = {t.due_date for t in scheduler.tasks if t.title == "Bath"}
    assert date.today() + timedelta(weeks=1) in dates


def test_generate_recurring_no_duplicates():
    scheduler = Scheduler()
    task = Task("Morning Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)

    scheduler.generate_recurring(days_ahead=3)
    count_before = len(scheduler.tasks)

    scheduler.generate_recurring(days_ahead=3)
    assert len(scheduler.tasks) == count_before


def test_non_recurring_task_not_expanded():
    scheduler = Scheduler()
    task = Task("One-off", "Single task", date.today(), "Biscuit",
                due_time=time(8, 0), duration_minutes=30, recurrence=None)
    scheduler.tasks.append(task)
    scheduler.generate_recurring(days_ahead=7)

    assert len(scheduler.tasks) == 1


# --- mark_task_complete: auto-scheduling ---

def test_mark_task_complete_marks_task_done():
    scheduler = Scheduler()
    task = Task("Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30)
    scheduler.tasks.append(task)

    scheduler.mark_task_complete(task)
    assert task.completed is True


def test_mark_task_complete_daily_creates_next_day():
    scheduler = Scheduler()
    task = Task("Morning Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.title == task.title
    assert next_task.completed is False


def test_mark_task_complete_weekly_creates_next_week():
    scheduler = Scheduler()
    task = Task("Bath", "Bath", date.today(), "Biscuit",
                due_time=time(10, 0), duration_minutes=30, recurrence="weekly")
    scheduler.tasks.append(task)

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_mark_task_complete_non_recurring_returns_none():
    scheduler = Scheduler()
    task = Task("Vet Visit", "Annual checkup", date.today(), "Biscuit",
                due_time=time(11, 0), duration_minutes=60, recurrence=None)
    scheduler.tasks.append(task)

    result = scheduler.mark_task_complete(task)
    assert result is None
    assert task.completed is True


def test_mark_task_complete_no_duplicate_if_next_exists():
    scheduler = Scheduler()
    today    = date.today()
    tomorrow = today + timedelta(days=1)

    task = Task("Morning Walk", "Walk", today, "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    next_existing = Task("Morning Walk", "Walk", tomorrow, "Biscuit",
                         due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.extend([task, next_existing])

    result = scheduler.mark_task_complete(task)
    assert result is None
    assert len([t for t in scheduler.tasks if t.title == "Morning Walk"]) == 2


# --- Conflict detection ---

def test_conflict_detection_warns_on_same_pet_overlap(capsys):
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0),  duration_minutes=60), scheduler)
    pet.add_task(Task("Bath", "Bath", date.today(), "", due_time=time(7, 30), duration_minutes=30), scheduler)

    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "Walk" in captured.out
    assert "Biscuit" in captured.out


def test_check_conflicts_returns_strings_not_exceptions():
    scheduler = Scheduler()
    pet1 = Pet(name="Biscuit", species="Dog", age=3)

    pet1.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0), duration_minutes=60), scheduler)
    overlap_task = Task("Playtime", "Play", date.today(), "Whiskers",
                        due_time=time(7, 0), duration_minutes=20)

    warnings = scheduler.check_conflicts(overlap_task)
    assert isinstance(warnings, list)
    assert len(warnings) == 1
    assert "can't do both" in warnings[0]


def test_check_conflicts_empty_when_no_overlap():
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0), duration_minutes=60), scheduler)
    later_task = Task("Feed", "Feed", date.today(), "Biscuit",
                      due_time=time(8, 0), duration_minutes=15)

    assert scheduler.check_conflicts(later_task) == []


def test_no_conflict_when_tasks_are_sequential(capsys):
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0),  duration_minutes=60), scheduler)
    pet.add_task(Task("Feed", "Feed", date.today(), "", due_time=time(8, 0),  duration_minutes=30), scheduler)

    captured = capsys.readouterr()
    assert "Warning" not in captured.out


def test_conflict_between_different_pets_warns(capsys):
    scheduler = Scheduler()
    pet1 = Pet(name="Biscuit",  species="Dog", age=3)
    pet2 = Pet(name="Whiskers", species="Cat", age=5)

    pet1.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0), duration_minutes=60), scheduler)
    pet2.add_task(Task("Meds", "Meds", date.today(), "", due_time=time(7, 0), duration_minutes=15), scheduler)

    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "Biscuit" in captured.out
    assert "Whiskers" in captured.out
    assert "can't do both" in captured.out
