import streamlit as st
from datetime import date, time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialisation ---
# Streamlit reruns the entire script on every interaction.
# Storing objects here keeps them alive between reruns.
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="")
if "pets" not in st.session_state:
    st.session_state.pets = {}          # pet_name -> Pet object

# ------------------------------------------------------------------ #
#  Header
# ------------------------------------------------------------------ #
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")
st.divider()

# ------------------------------------------------------------------ #
#  Section 1 — Owner Info
# ------------------------------------------------------------------ #
st.subheader("👤 Owner Info")

with st.form("owner_form"):
    owner_name  = st.text_input("Your name",  value=st.session_state.owner.name)
    owner_email = st.text_input("Your email", value=st.session_state.owner.email)
    if st.form_submit_button("Save owner info"):
        st.session_state.owner.name  = owner_name
        st.session_state.owner.email = owner_email
        st.success(f"Saved! Welcome, {owner_name}.")

st.divider()

# ------------------------------------------------------------------ #
#  Section 2 — Add a Pet
# ------------------------------------------------------------------ #
st.subheader("🐶 Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name")
    species  = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    age      = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

    if st.form_submit_button("Add pet"):
        if not pet_name:
            st.warning("Please enter a pet name.")
        elif pet_name in st.session_state.pets:
            st.warning(f"{pet_name} is already in your list.")
        else:
            new_pet = Pet(name=pet_name, species=species, age=int(age))
            st.session_state.owner.add_pet(new_pet)
            st.session_state.pets[pet_name] = new_pet
            st.success(f"Added {pet_name} the {species}!")

if st.session_state.pets:
    st.markdown("**Your pets:**")
    for pet in st.session_state.owner.view_pets():
        st.write(f"- {pet.name} ({pet.species}, age {pet.age})")

st.divider()

# ------------------------------------------------------------------ #
#  Section 3 — Add a Task
# ------------------------------------------------------------------ #
st.subheader("📋 Add a Task")

if not st.session_state.pets:
    st.info("Add at least one pet above before adding tasks.")
else:
    with st.form("task_form"):
        col_left, col_right = st.columns(2)
        with col_left:
            selected_pet  = st.selectbox("Assign to pet", list(st.session_state.pets.keys()))
            task_title    = st.text_input("Task title", value="Morning walk")
            task_desc     = st.text_input("Description", value="")
        with col_right:
            task_due_date = st.date_input("Due date", value=date.today())
            task_due_time = st.time_input("Time", value=time(8, 0))
            task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)

        task_recurrence = st.selectbox(
            "Recurrence",
            ["None", "daily", "weekly"],
            help="Daily and weekly tasks auto-schedule their next occurrence when marked done.",
        )
        submitted = st.form_submit_button("Add task")

    # Handle submission outside the form so st.warning / st.success render correctly
    if submitted:
        if not task_title:
            st.warning("Please enter a task title.")
        else:
            recurrence_val = None if task_recurrence == "None" else task_recurrence
            new_task = Task(
                title=task_title,
                description=task_desc,
                due_date=task_due_date,
                pet_name=selected_pet,
                due_time=task_due_time,
                duration_minutes=int(task_duration),
                recurrence=recurrence_val,
            )

            # --- Conflict detection: check BEFORE adding, surface in the UI ---
            # check_conflicts() returns human-readable strings, never raises.
            conflicts = st.session_state.scheduler.check_conflicts(new_task)
            for conflict_msg in conflicts:
                st.warning(
                    f"⚠️ **Scheduling conflict:** {conflict_msg}\n\n"
                    f"The task has been added, but you may want to adjust the time."
                )

            pet = st.session_state.pets[selected_pet]
            pet.add_task(new_task, st.session_state.scheduler)

            if not conflicts:
                time_str = task_due_time.strftime("%H:%M")
                st.success(f"✅ '{task_title}' added for {selected_pet} at {time_str}!")
            else:
                st.info("Task added — see conflict warning above.")

st.divider()

# ------------------------------------------------------------------ #
#  Section 4 — Today's Schedule
# ------------------------------------------------------------------ #
st.subheader("📅 Today's Schedule")

scheduler    = st.session_state.scheduler
all_today    = scheduler.get_today_tasks()   # Scheduler.get_today_tasks() — already sorted by time

if not all_today:
    st.info("No tasks due today. Add some tasks with today's date.")
else:
    # --- Filter controls ---
    col_a, col_b = st.columns(2)
    with col_a:
        pet_options = ["All pets"] + sorted({t.pet_name for t in all_today})
        filter_pet  = st.selectbox("Filter by pet", pet_options, key="filter_pet")
    with col_b:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Pending", "Done"], key="filter_status"
        )

    # Translate UI selections into Scheduler.filter_tasks() arguments
    pet_arg  = None if filter_pet == "All pets" else filter_pet
    done_arg = None if filter_status == "All" else (filter_status == "Done")

    # filter_tasks() does a single-pass match; sort_by_time() returns a new sorted list
    tasks_shown = scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name=pet_arg, completed=done_arg, on_date=date.today())
    )

    # --- Summary metrics ---
    done_count    = sum(1 for t in all_today if t.completed)
    pending_count = len(all_today) - done_count

    m1, m2, m3 = st.columns(3)
    m1.metric("Total today",  len(all_today))
    m2.metric("✅ Done",      done_count)
    m3.metric("🔲 Pending",   pending_count)

    st.caption(
        f"Showing {len(tasks_shown)} of {len(all_today)} tasks · "
        f"sorted chronologically by time"
    )
    st.divider()

    # --- Task cards ---
    if not tasks_shown:
        st.info("No tasks match the current filter.")

    for task in tasks_shown:
        with st.container(border=True):
            card_left, card_right = st.columns([5, 1])

            with card_left:
                time_str = task.due_time.strftime("%H:%M")
                badge    = "✅" if task.completed else "🔲"

                if task.completed:
                    st.markdown(
                        f"{badge} ~~**{task.title}**~~ · *{task.pet_name}* · "
                        f"`{time_str}` · {task.duration_minutes} min"
                    )
                else:
                    st.markdown(
                        f"{badge} **{task.title}** · *{task.pet_name}* · "
                        f"`{time_str}` · {task.duration_minutes} min"
                    )

                if task.description:
                    st.caption(task.description)

                if task.recurrence:
                    st.caption(f"🔁 Repeats {task.recurrence}")

            with card_right:
                if not task.completed:
                    # Unique key prevents Streamlit confusing buttons across reruns
                    btn_key = f"done_{task.pet_name}_{task.title}_{task.due_date}_{task.due_time}"
                    if st.button("✓ Done", key=btn_key, use_container_width=True):
                        # mark_task_complete() marks done AND auto-schedules next occurrence
                        next_task = scheduler.mark_task_complete(task)
                        if next_task:
                            st.success(
                                f"Done! '{task.title}' auto-scheduled for "
                                f"**{next_task.due_date}** (recurring {task.recurrence})."
                            )
                        else:
                            st.success("Marked as done!")
                        st.rerun()   # re-render the schedule with updated status
