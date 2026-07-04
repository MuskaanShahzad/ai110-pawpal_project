from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(tasks: list) -> None:
    if not tasks:
        print("  No tasks scheduled for today.")
        return
    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        print(f"  {status}  {task.pet_name:<12} {task.title}")
        print(f"             {task.description}")
        print()


def main() -> None:
    scheduler = Scheduler()

    # --- Set up owner and pets ---
    owner = Owner(name="Muskaan", email="muskaan@example.com")

    biscuit  = Pet(name="Biscuit",  species="Dog", age=3)
    whiskers = Pet(name="Whiskers", species="Cat", age=5)

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    # --- Add tasks (mix of today and tomorrow) ---
    today    = date.today()
    tomorrow = today + timedelta(days=1)

    biscuit.add_task(
        Task("Morning Walk", "30-min walk around the block", today, ""),
        scheduler,
    )
    biscuit.add_task(
        Task("Feeding", "1 cup of dry food, morning serving", today, ""),
        scheduler,
    )
    whiskers.add_task(
        Task("Medication", "Give joint supplement pill with food", today, ""),
        scheduler,
    )
    whiskers.add_task(
        Task("Grooming", "Brush fur for 10 minutes", tomorrow, ""),
        scheduler,
    )

    # Mark the walk as already done (for demo purposes)
    scheduler.tasks[0].mark_complete()

    # --- Print today's schedule ---
    today_tasks = scheduler.get_today_tasks()

    print("=" * 48)
    print("         PawPal+ - Today's Schedule")
    print("=" * 48)
    print(f"  Owner : {owner.name}  |  {owner.email}")
    print(f"  Pets  : {', '.join(p.name for p in owner.view_pets())}")
    print(f"  Date  : {today}")
    print("=" * 48)
    print()

    print_schedule(today_tasks)

    done    = sum(1 for t in today_tasks if t.completed)
    pending = len(today_tasks) - done

    print("=" * 48)
    print(f"  Today: {len(today_tasks)} task(s)  |  Done: {done}  |  Pending: {pending}")
    print("=" * 48)


if __name__ == "__main__":
    main()
