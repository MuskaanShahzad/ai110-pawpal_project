# PawPal+ Project Reflection

## 1. System Design

**a. Core User Actions**

- The user can add and manage pets by entering information such as the pet's name, species, and age.
- The user can create and schedule pet care tasks, such as feeding, walking, grooming, or giving medication.
- The user can view today's scheduled tasks to keep track of what needs to be completed for each pet.

**b. Initial design**

My initial UML design includes four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- **Owner** represents a user of the app. It holds the owner's name and email, and maintains a list of their pets. It is responsible for adding, removing, and viewing pets.
- **Pet** represents an individual animal belonging to an owner. It stores the pet's name, species, and age, and holds a list of tasks assigned to that pet. It can add new tasks and display existing ones.
- **Task** represents a single care action (such as feeding or walking). It stores a title, description, due date, the associated pet's name, and a completion status. It can be marked complete or incomplete.
- **Scheduler** acts as a central manager for all tasks across all pets. It can add tasks and filter them by today's date or by a specific pet's name.

The main relationships are: an Owner owns zero or more Pets, a Pet has zero or more Tasks, and the Scheduler manages all Tasks.

**c. Design changes**

Two changes were made after an AI review of the skeleton:

1. **Changed `due_date` from `str` to `datetime.date`** — The original design stored due dates as plain strings. Since `get_today_tasks()` needs to compare dates, using Python's built-in `date` type makes that comparison safe and accurate without needing to manually parse strings.

2. **Removed `tasks` list from `Pet` and made `Scheduler` the single source of truth** — The original design stored tasks in both `Pet.tasks` and `Scheduler.tasks`, which could easily fall out of sync if one list was updated but not the other. Now `Pet.add_task()` and `Pet.view_tasks()` both accept a `Scheduler` parameter and delegate to it, so all tasks live in one place.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two primary constraints: **time** (when a task is scheduled via `due_time`) and **duration** (how long it takes via `duration_minutes`). Together these define a task's time window, which is what the conflict detection algorithm uses to check for overlaps.

I decided these two mattered most because a pet owner's day is physically structured around time slots — you either are or aren't available at 7:00 AM to walk the dog. A conflict in time is the most immediate and concrete problem to solve. Priority (high vs. low urgency) and preference (owner's preferred routine order) were considered but left for a future iteration, because implementing them well would require ranking tasks against each other, which is a significantly more complex algorithm. Starting with time-window constraints gave the scheduler real value without over-engineering it.

**b. Tradeoffs**

**Tradeoff: linear scan for conflict detection vs. indexed lookup**

The scheduler's `_conflicts()` method loops through every task in `self.tasks` for each new task being added. This is O(n) per conflict check, making the overall cost of adding n tasks O(n²). A more scalable design would index tasks by date — for example, a dictionary mapping `due_date → List[Task]` — so each check only scans the tasks scheduled for that specific day rather than the entire list.

The reason a plain list is reasonable here is that a personal pet scheduling app will realistically hold tens of tasks, not thousands. At that scale the linear scan completes in microseconds, and the simpler data structure is easier to reason about, iterate over, and serialize. Adding an index would require keeping it in sync whenever a task's date changes or a task is removed — complexity that would only pay off at a much larger scale. The tradeoff is **simplicity and maintainability now** in exchange for **scalability later**.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude as a collaborative coding assistant across every phase of this project, but in different ways depending on the task:

- **Design brainstorming (Phase 1–2):** I asked open-ended questions like "what algorithms or logic improvements would make a pet scheduling app smarter?" This produced a concrete feature list (sorting, filtering, recurring tasks, conflict detection) that became the Phase 3 roadmap. The most helpful prompts were goal-oriented rather than code-specific — asking *what* to build before asking *how*.

- **Implementation (Phase 3–4):** I gave Claude access to the relevant files and asked it to implement specific features one step at a time. Keeping each step narrow ("now implement just the sort method") produced cleaner code than asking for everything at once. Claude also handled the boilerplate-heavy parts (writing 37 test cases, updating docstrings, filling README tables) so I could focus on reviewing and understanding each change.

- **Refactoring (Phase 4 Step 5):** I asked Claude to evaluate a completed method and suggest simplifications. This produced two genuine improvements: replacing a verbose `Task(title=task.title, description=task.description, ...)` block with `dataclasses.replace()`, and collapsing a multi-pass filter into a single list comprehension. Both were more correct *and* more readable, so I kept them.

- **Testing strategy (Phase 5):** The most useful prompt here was "what are the most important edge cases to test for a pet scheduler?" rather than "write me some tests." Getting the test *plan* first helped me understand which gaps existed before writing any code.

**b. Judgment and verification**

During Phase 4 Step 5 (Evaluate and Refine), Claude suggested replacing the `if/elif` recurrence check in `generate_recurring` with a one-liner dict lookup:

```python
# AI suggestion
delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}[task.recurrence]
```

I chose not to accept this version. While it is more "Pythonic" in the sense of being concise, it would raise a `KeyError` if an unrecognized recurrence value ever appeared (like `"monthly"`), crashing the program instead of gracefully skipping the task. The `if/elif` version with an explicit `else: continue` is safer and clearer about what happens with unknown values. I verified this was the right call by checking what our test `test_generate_recurring_unknown_recurrence_skipped` expected — it confirmed the correct behavior is a silent skip, not an exception.

---

## 4. Testing and Verification

**a. What you tested**

The final test suite contains 37 tests across six behavioral areas:

1. **Task status** — `mark_complete` and `mark_incomplete` toggle `completed` correctly and independently.
2. **Sorting** — tasks added out of order appear chronologically in `get_today_tasks()`; `sort_by_time([])` handles an empty list; two tasks at the same time preserve stable insertion order.
3. **Filtering** — `filter_tasks()` correctly handles every combination of pet name, status, and date; returns empty list (not an error) for unknown pets or empty schedulers; returns all tasks when called with no arguments.
4. **Recurring tasks** — daily and weekly auto-scheduling creates the correct next date; completing a task twice doesn't create a third copy; `days_ahead=0` generates nothing; an unknown recurrence value like `"monthly"` is silently skipped.
5. **Conflict detection** — overlapping tasks warn for both same-pet and cross-pet cases; sequential tasks (one ending exactly when the next begins) produce no false warning; tasks on different dates at the same clock time produce no conflict.
6. **Boundary and empty states** — `get_today_tasks()`, `get_tasks_by_pet()`, and `get_tasks_by_owner()` all return `[]` rather than crashing when there is nothing to return.

These tests mattered because the most dangerous bugs in a scheduler are silent — they don't crash the program, they just produce wrong output. The edge case tests (especially the "late completion uses `due_date` not `today`" test) would catch bugs that might never appear in normal use but would corrupt a user's schedule in exactly the wrong moment.

**b. Confidence**

**★★★★☆ (4 / 5).** I am confident the core scheduling logic is correct — all 37 tests pass, they cover both expected behavior and boundary conditions, and the tests were written to be meaningful rather than just to hit coverage numbers.

The missing star reflects that the tests run against in-memory data only. If I had more time, I would test next:
- The Streamlit UI behavior (e.g., does the conflict warning actually appear on screen when it should?)
- Persistence across sessions (tasks currently vanish when the browser refreshes)
- Performance with a larger task list (100+ tasks) to validate the linear-scan tradeoff discussed in section 2b

---

## 5. Reflection

**a. What went well**

I am most satisfied with the conflict detection design. The decision to make `check_conflicts()` return a list of strings rather than printing directly or raising an exception made the method genuinely reusable — the CLI demo prints them, the Streamlit UI surfaces them as `st.warning` banners, and the tests can assert on their content without capturing stdout. That one design choice meant the same logic worked cleanly across three different contexts without any modification.

I am also proud of how the test suite came together. Starting with a gap analysis (what is already covered vs. what is missing) before writing any code produced a more thoughtful suite than if I had just asked for tests immediately. The "late completion uses `due_date` not `today`" test in particular captures a real-world bug that would be easy to miss.

**b. What you would improve**

If I had another iteration, I would redesign two things:

1. **Task persistence.** Right now all tasks live in `st.session_state` and disappear when the browser refreshes. I would add a simple JSON file as a persistence layer — `Scheduler.save()` and `Scheduler.load()` — so a pet owner's schedule survives between sessions.

2. **Priority as a scheduling constraint.** The current scheduler sorts only by time. A real improvement would be a `priority` field on `Task` (high / medium / low) that `sort_by_time` uses as a tiebreaker when two tasks share the same time slot. This would make the "daily plan" feel more like an intelligent recommendation than a plain sorted list.

**c. Key takeaway**

The most important thing I learned is that **AI is a powerful implementer but a poor architect.** Claude could write a correct `sort_by_time` method in seconds, generate 37 tests, and refactor a method to use `dataclasses.replace()`. But it could not decide *which* features belonged in this app, *which* tradeoffs were acceptable for a personal-use tool, or *when* to stop adding complexity. Every meaningful design decision in this project — removing `tasks` from `Pet`, choosing time-window conflict detection over priority scoring, keeping `if/elif` instead of the one-liner dict — required me to reason about the problem, not just the code.

Using separate chat sessions for different phases reinforced this. Each session had a clear goal, which forced me to understand what I had already built before asking for the next thing. If I had treated AI as a single continuous "do everything" tool, I would have ended up with a system I couldn't explain. Instead, I can describe every method, every tradeoff, and every test because I reviewed and approved each one. That's what being the lead architect means: you own the *why*, even when AI writes the *how*.
