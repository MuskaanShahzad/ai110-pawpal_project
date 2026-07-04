from datetime import date, timedelta, time
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(tasks: list) -> None:
    if not tasks:
        print("  No tasks scheduled.")
        return
    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        time_str = task.due_time.strftime("%H:%M")
        print(f"  {status}  {time_str}  {task.pet_name:<12} {task.title}")
        print(f"                   {task.description}")
        print()


def main() -> None:
    scheduler = Scheduler()

    # --- Set up owner and pets ---
    owner = Owner(name="Muskaan", email="muskaan@example.com")

    biscuit  = Pet(name="Biscuit",  species="Dog", age=3)
    whiskers = Pet(name="Whiskers", species="Cat", age=5)

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    today    = date.today()
    tomorrow = today + timedelta(days=1)

    # --- Add tasks out of order to demonstrate sorting ---
    whiskers.add_task(
        Task("Medication", "Give joint supplement pill with food", today, "",
             due_time=time(9, 0), duration_minutes=10),
        scheduler,
    )
    biscuit.add_task(
        Task("Feeding", "1 cup of dry food, morning serving", today, "",
             due_time=time(8, 0), duration_minutes=15),
        scheduler,
    )
    biscuit.add_task(
        Task("Morning Walk", "30-min walk around the block", today, "",
             due_time=time(7, 0), duration_minutes=30, recurrence="daily"),
        scheduler,
    )
    whiskers.add_task(
        Task("Grooming", "Brush fur for 10 minutes", tomorrow, "",
             due_time=time(10, 0), duration_minutes=10),
        scheduler,
    )

    # --- Header ---
    print("=" * 52)
    print("           PawPal+ - Today's Schedule")
    print("=" * 52)
    print(f"  Owner : {owner.name}  |  {owner.email}")
    print(f"  Pets  : {', '.join(p.name for p in owner.view_pets())}")
    print(f"  Date  : {today}")
    print("=" * 52)

    # --- Full schedule sorted by time ---
    print("\n  [All tasks - sorted by time]")
    today_tasks = scheduler.get_today_tasks()
    print_schedule(today_tasks)

    # --- Filtered: pending tasks only ---
    print("  [Pending tasks only]")
    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False, on_date=today))
    print_schedule(pending)

    # --- Filtered: Biscuit's tasks only ---
    print("  [Biscuit's tasks only]")
    biscuit_tasks = scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit", on_date=today))
    print_schedule(biscuit_tasks)

    # --- Conflict detection demo ---
    # Same-pet conflict: Bath at 07:15 overlaps Biscuit's Walk at 07:00 (30 min)
    print("  [Adding conflicting tasks — watch for warnings]")
    biscuit.add_task(
        Task("Bath", "Quick rinse after walk", today, "",
             due_time=time(7, 15), duration_minutes=30),
        scheduler,
    )
    # Cross-pet conflict: Playtime at 07:00 overlaps Biscuit's Walk — owner can't do both
    whiskers.add_task(
        Task("Playtime", "Interactive toy session", today, "",
             due_time=time(7, 0), duration_minutes=20),
        scheduler,
    )
    print()

    # --- Mark walk complete: auto-schedules tomorrow's walk via timedelta ---
    walk = scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit", on_date=today))[0]
    next_walk = scheduler.mark_task_complete(walk)

    print("  [Recurring task completed]")
    print(f"  Marked done : '{walk.title}' on {walk.due_date}")
    if next_walk:
        print(f"  Auto-created: '{next_walk.title}' on {next_walk.due_date}  "
              f"(today + 1 day via timedelta)")
    print()

    # --- Summary ---
    done          = sum(1 for t in today_tasks if t.completed)
    pending_count = len(today_tasks) - done
    tomorrow_count = len(scheduler.filter_tasks(on_date=tomorrow))

    print("=" * 52)
    print(f"  Today: {len(today_tasks)} task(s)  |  Done: {done}  |  Pending: {pending_count}")
    print(f"  Tomorrow: {tomorrow_count} task(s) scheduled (incl. auto-generated)")
    print("=" * 52)


if __name__ == "__main__":
    main()
