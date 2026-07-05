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


# =============================================================================
# Phase 5 — edge-case suite
# Each section targets one behavior from the test plan and covers both the
# happy path (works correctly) and the edge case (boundary / unexpected input).
# =============================================================================

# --- Sorting edge cases ---

def test_sort_by_time_empty_list():
    # sorted() on an empty list must return [] — not raise an error.
    # This guards against callers passing an empty filter result into sort_by_time.
    scheduler = Scheduler()
    assert scheduler.sort_by_time([]) == []


def test_sort_by_time_same_time_is_stable():
    # Python's sorted() is guaranteed stable: equal elements keep their original order.
    # Two tasks at 07:00 should come back Walk → Feed (insertion order), never swapped.
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)

    pet.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0), duration_minutes=0), scheduler)
    pet.add_task(Task("Feed", "Feed", date.today(), "", due_time=time(7, 0), duration_minutes=0), scheduler)

    tasks = scheduler.sort_by_time(scheduler.get_today_tasks())
    assert len(tasks) == 2
    assert tasks[0].title == "Walk"   # first inserted comes first
    assert tasks[1].title == "Feed"


# --- Filtering edge cases ---

def test_filter_tasks_no_arguments_returns_all():
    # Calling filter_tasks() with no arguments means "no filters applied".
    # Every task in the scheduler should be returned.
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    pet.add_task(make_task("Walk"), scheduler)
    pet.add_task(make_task("Feed"), scheduler)

    assert len(scheduler.filter_tasks()) == 2


def test_filter_tasks_unknown_pet_returns_empty():
    # If no tasks belong to the requested pet, the result should be an empty
    # list — not None, not an error.
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    pet.add_task(make_task("Walk"), scheduler)

    assert scheduler.filter_tasks(pet_name="Ghost") == []


def test_filter_tasks_on_empty_scheduler():
    # All filter combinations on a scheduler with zero tasks must return [].
    scheduler = Scheduler()
    assert scheduler.filter_tasks(pet_name="Biscuit") == []
    assert scheduler.filter_tasks(completed=False) == []
    assert scheduler.filter_tasks(on_date=date.today()) == []


# --- Recurring edge cases ---

def test_mark_task_complete_twice_no_double_schedule():
    # Calling mark_task_complete on the same task twice should NOT create two
    # copies of the next occurrence — the second call detects it already exists.
    scheduler = Scheduler()
    task = Task("Morning Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)

    scheduler.mark_task_complete(task)        # creates tomorrow's task
    second_result = scheduler.mark_task_complete(task)  # tomorrow already exists

    assert second_result is None
    walk_count = len([t for t in scheduler.tasks if t.title == "Morning Walk"])
    assert walk_count == 2   # today (done) + tomorrow, never three


def test_mark_task_complete_uses_due_date_not_today():
    # If a task was due yesterday and is completed late, the next occurrence
    # should be due_date + 1 day (= today), NOT date.today() + 1 day (= tomorrow).
    # This prevents late completions from silently shifting the schedule forward.
    scheduler = Scheduler()
    yesterday = date.today() - timedelta(days=1)

    task = Task("Walk", "Walk", yesterday, "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)

    next_task = scheduler.mark_task_complete(task)

    # yesterday + 1 day = today — completing late does not skip today
    assert next_task.due_date == date.today()


def test_generate_recurring_days_ahead_zero():
    # days_ahead=0 means the deadline is today itself. The first candidate date
    # is always due_date + delta (= tomorrow for a daily task), which is already
    # past the deadline, so the while-loop should never execute.
    scheduler = Scheduler()
    task = Task("Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=30, recurrence="daily")
    scheduler.tasks.append(task)

    scheduler.generate_recurring(days_ahead=0)

    assert len(scheduler.tasks) == 1   # no new tasks added


def test_generate_recurring_unknown_recurrence_skipped():
    # "monthly" is not a supported recurrence value. The scheduler should
    # silently ignore it rather than crash or create incorrect occurrences.
    scheduler = Scheduler()
    task = Task("Vet", "Annual vet visit", date.today(), "Biscuit",
                due_time=time(10, 0), duration_minutes=60, recurrence="monthly")
    scheduler.tasks.append(task)

    scheduler.generate_recurring(days_ahead=31)

    assert len(scheduler.tasks) == 1   # "monthly" task untouched


# --- Conflict edge cases ---

def test_no_conflict_same_time_different_dates():
    # Two tasks at 07:00 but on different dates must NOT produce a conflict.
    # Conflict detection only considers tasks on the same calendar date.
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    tomorrow = date.today() + timedelta(days=1)

    pet.add_task(Task("Walk", "Walk", date.today(), "", due_time=time(7, 0), duration_minutes=60), scheduler)
    tomorrows_task = Task("Walk", "Walk", tomorrow, "Biscuit",
                          due_time=time(7, 0), duration_minutes=60)

    assert scheduler.check_conflicts(tomorrows_task) == []


def test_check_conflicts_on_empty_scheduler():
    # With no existing tasks, conflict detection should always return an
    # empty list — there is nothing to conflict with.
    scheduler = Scheduler()
    task = Task("Walk", "Walk", date.today(), "Biscuit",
                due_time=time(7, 0), duration_minutes=60)

    assert scheduler.check_conflicts(task) == []


# --- Empty / boundary states ---

def test_get_today_tasks_on_empty_scheduler():
    # An empty scheduler has no tasks; get_today_tasks should return [],
    # not raise an IndexError or return None.
    scheduler = Scheduler()
    assert scheduler.get_today_tasks() == []


def test_get_tasks_by_pet_unknown_pet():
    # Asking for tasks belonging to a pet that has never been added should
    # return an empty list rather than crash.
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="Dog", age=3)
    pet.add_task(make_task("Walk"), scheduler)

    assert scheduler.get_tasks_by_pet("Ghost") == []


def test_get_tasks_by_owner_no_pets():
    # An owner with zero pets has no tasks. get_tasks_by_owner should return []
    # without touching self.tasks at all (empty pet_names set matches nothing).
    scheduler = Scheduler()
    owner = Owner(name="Muskaan", email="muskaan@example.com")

    assert scheduler.get_tasks_by_owner(owner) == []
