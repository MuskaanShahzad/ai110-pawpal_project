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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
