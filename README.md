# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
====================================================
           PawPal+ - Today's Schedule
====================================================
  Owner : Muskaan  |  muskaan@example.com
  Pets  : Biscuit, Whiskers
  Date  : 2026-07-03
====================================================

  [All tasks - sorted by time]
  [ ]  07:00  Biscuit      Morning Walk
                   30-min walk around the block

  [ ]  08:00  Biscuit      Feeding
                   1 cup of dry food, morning serving

  [ ]  09:00  Whiskers     Medication
                   Give joint supplement pill with food

  [Pending tasks only]
  [ ]  07:00  Biscuit      Morning Walk
  [ ]  09:00  Whiskers     Medication

  [Recurring task completed]
  Marked done : 'Morning Walk' on 2026-07-03
  Auto-created: 'Morning Walk' on 2026-07-04  (today + 1 day via timedelta)

====================================================
  Today: 3 task(s)  |  Done: 1  |  Pending: 2
  Tomorrow: 2 task(s) scheduled (incl. auto-generated)
====================================================
```

## 🧪 Testing PawPal+

### Run the tests

```bash
# Run the full test suite with verbose output:
python -m pytest tests/test_pawpal.py -v

# Run without verbose (summary only):
python -m pytest tests/test_pawpal.py
```

### What the tests cover

The suite contains **37 tests** across five behavioral areas:

| Area | # Tests | What's verified |
|------|---------|-----------------|
| **Task status** | 2 | `mark_complete` and `mark_incomplete` toggle correctly |
| **Sorting** | 4 | Tasks added out of order appear chronologically; empty list and same-time ties are handled safely |
| **Filtering** | 5 | Filter by pet, status, date, any combination, and edge cases (unknown pet, no arguments, empty scheduler) |
| **Recurring tasks** | 8 | Daily and weekly auto-scheduling; duplicate prevention; `days_ahead=0`; late completions use `due_date` not `today`; unknown recurrence values silently skipped |
| **Conflict detection** | 7 | Same-pet and cross-pet overlaps produce warnings; sequential tasks, different dates, and empty scheduler produce no false positives |
| **Boundary / empty states** | 5 | Empty scheduler, unknown pet, owner with no pets — all return `[]` without crashing |
| **Core integration** | 6 | Adding tasks increases counts; `get_today_tasks` excludes tomorrow; `get_tasks_by_owner` scopes correctly |

### Test output

```
============================= test session starts =============================
platform win32 -- Python 3.10.2, pytest-9.1.1, pluggy-1.6.0
collected 37 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  2%]
tests/test_pawpal.py::test_mark_incomplete_changes_status PASSED         [  5%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  8%]
tests/test_pawpal.py::test_get_today_tasks_sorted_by_time PASSED         [ 10%]
tests/test_pawpal.py::test_tomorrow_tasks_excluded_from_today PASSED     [ 13%]
tests/test_pawpal.py::test_filter_by_pet PASSED                          [ 16%]
tests/test_pawpal.py::test_filter_by_completed_status PASSED             [ 18%]
tests/test_pawpal.py::test_filter_combined_pet_and_status PASSED         [ 21%]
tests/test_pawpal.py::test_filter_by_date PASSED                         [ 24%]
tests/test_pawpal.py::test_generate_recurring_daily_creates_future_tasks PASSED [ 27%]
tests/test_pawpal.py::test_generate_recurring_weekly_creates_correct_date PASSED [ 29%]
tests/test_pawpal.py::test_generate_recurring_no_duplicates PASSED       [ 32%]
tests/test_pawpal.py::test_non_recurring_task_not_expanded PASSED        [ 35%]
tests/test_pawpal.py::test_mark_task_complete_marks_task_done PASSED     [ 37%]
tests/test_pawpal.py::test_mark_task_complete_daily_creates_next_day PASSED [ 40%]
tests/test_pawpal.py::test_mark_task_complete_weekly_creates_next_week PASSED [ 43%]
tests/test_pawpal.py::test_mark_task_complete_non_recurring_returns_none PASSED [ 45%]
tests/test_pawpal.py::test_mark_task_complete_no_duplicate_if_next_exists PASSED [ 48%]
tests/test_pawpal.py::test_conflict_detection_warns_on_same_pet_overlap PASSED [ 51%]
tests/test_pawpal.py::test_check_conflicts_returns_strings_not_exceptions PASSED [ 54%]
tests/test_pawpal.py::test_check_conflicts_empty_when_no_overlap PASSED  [ 56%]
tests/test_pawpal.py::test_no_conflict_when_tasks_are_sequential PASSED  [ 59%]
tests/test_pawpal.py::test_conflict_between_different_pets_warns PASSED  [ 62%]
tests/test_pawpal.py::test_sort_by_time_empty_list PASSED                [ 64%]
tests/test_pawpal.py::test_sort_by_time_same_time_is_stable PASSED       [ 67%]
tests/test_pawpal.py::test_filter_tasks_no_arguments_returns_all PASSED  [ 70%]
tests/test_pawpal.py::test_filter_tasks_unknown_pet_returns_empty PASSED [ 72%]
tests/test_pawpal.py::test_filter_tasks_on_empty_scheduler PASSED        [ 75%]
tests/test_pawpal.py::test_mark_task_complete_twice_no_double_schedule PASSED [ 78%]
tests/test_pawpal.py::test_mark_task_complete_uses_due_date_not_today PASSED [ 81%]
tests/test_pawpal.py::test_generate_recurring_days_ahead_zero PASSED     [ 83%]
tests/test_pawpal.py::test_generate_recurring_unknown_recurrence_skipped PASSED [ 86%]
tests/test_pawpal.py::test_no_conflict_same_time_different_dates PASSED  [ 89%]
tests/test_pawpal.py::test_check_conflicts_on_empty_scheduler PASSED     [ 91%]
tests/test_pawpal.py::test_get_today_tasks_on_empty_scheduler PASSED     [ 94%]
tests/test_pawpal.py::test_get_tasks_by_pet_unknown_pet PASSED           [ 97%]
tests/test_pawpal.py::test_get_tasks_by_owner_no_pets PASSED             [100%]

============================= 37 passed in 0.07s ==============================
```

### Confidence level

**★★★★☆ (4 / 5)**

All 37 tests pass, covering both happy paths and edge cases for every scheduling algorithm. Confidence is strong for the core Python logic. One star is held back because the tests run against in-memory data only — the Streamlit UI layer and any future persistence (database, file) have not yet been tested end-to-end.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(tasks)` | Sorts any list of Tasks by `due_time` using a lambda key; called automatically by `get_today_tasks()` so today's schedule is always in chronological order |
| Filtering | `Scheduler.filter_tasks(pet_name, completed, on_date)` | Single-pass filter accepting any combination of pet, completion status, and date; omit a parameter to leave that dimension unfiltered |
| Conflict detection | `Scheduler.check_conflicts(task)` | Returns a list of warning strings (never raises) for same-pet **and** cross-pet time overlaps; called automatically on every `add_task()` so conflicts surface at scheduling time |
| Recurring tasks | `Scheduler.mark_task_complete(task)` | Marks a task done and uses `timedelta` to auto-schedule the next occurrence from `due_date` (not today), so late completions don't shift the schedule |
| Bulk recurring expansion | `Scheduler.generate_recurring(days_ahead)` | Pre-generates all future occurrences up to `days_ahead` days out; skips dates that already exist to prevent duplicates |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
