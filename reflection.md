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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
