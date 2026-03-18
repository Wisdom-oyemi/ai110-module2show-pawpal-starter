import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app!
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

"""
    )

st.divider()

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")
owner_email = st.text_input("Owner email", value="jordan@example.com")
available_time = st.number_input(
    "Available time per day (minutes)",
    min_value=1,
    max_value=600,
    value=60,
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name,
        email=owner_email,
        available_time_per_day=float(available_time),
    )

if st.button("Update owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        email=owner_email,
        available_time_per_day=float(available_time),
    )
    st.success("Owner profile updated.")

owner: Owner = st.session_state.owner

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="Mixed")
age = st.number_input("Age", min_value=0.0, max_value=40.0, value=3.0, step=0.5)
health_conditions_raw = st.text_input(
    "Health conditions (comma-separated)",
    value="",
)

if st.button("Add pet"):
    health_conditions = [
        condition.strip()
        for condition in health_conditions_raw.split(",")
        if condition.strip()
    ]
    new_pet = Pet(
        name=pet_name,
        species=species,
        breed=breed,
        age=float(age),
        health_conditions=health_conditions,
    )
    owner.add_pet(new_pet)
    st.success(f"Added pet: {new_pet.name}")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "age": pet.age,
                "health_conditions": ", ".join(pet.health_conditions) or "None",
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Create tasks and assign them to an existing pet.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["high", "medium", "low"], index=0)

category = st.text_input("Task category", value="exercise")
recurrence = st.selectbox("Recurrence", ["daily", "weekly", "as needed"], index=0)

if owner.pets:
    pet_options = {f"{pet.name} ({pet.species})": pet for pet in owner.pets}
    selected_pet_label = st.selectbox("Assign to pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_label]
else:
    selected_pet = None
    st.warning("Add a pet before creating tasks.")

priority_map = {"high": 1, "medium": 3, "low": 5}

if st.button("Add task") and selected_pet is not None:
    task = Task(
        name=task_title,
        category=category,
        duration=float(duration),
        priority=priority_map[priority_label],
        pet=selected_pet,
        recurrence=recurrence,
    )
    owner.add_task(task)
    st.success(f"Added task: {task.name} for {selected_pet.name}")

if owner.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.name,
                "pet": task.pet.name if task.pet else "Unassigned",
                "category": task.category,
                "duration_minutes": task.duration,
                "priority": task.priority,
                "recurrence": task.recurrence,
                "status": task.status,
            }
            for task in owner.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a sorted and filtered daily plan using scheduler rules.")

if owner.scheduler is None:
    owner.scheduler = Scheduler(owner)

available_categories = sorted({task.category for task in owner.tasks})
available_pet_names = sorted({task.pet.name for task in owner.tasks if task.pet is not None})

fcol1, fcol2 = st.columns(2)
with fcol1:
    selected_categories = st.multiselect(
        "Filter categories",
        options=available_categories,
        default=available_categories,
    )
with fcol2:
    selected_pets = st.multiselect(
        "Filter pets",
        options=available_pet_names,
        default=available_pet_names,
    )

fcol3, fcol4 = st.columns(2)
with fcol3:
    max_priority = st.selectbox(
        "Highest priority number to include (1 is most urgent)",
        options=[1, 2, 3, 4, 5],
        index=4,
    )
with fcol4:
    schedule_time_limit = st.number_input(
        "Schedule time limit (minutes)",
        min_value=1,
        max_value=600,
        value=int(owner.available_time_per_day),
    )

if st.button("Generate schedule"):
    constraints = {
        "max_time": float(schedule_time_limit),
        "max_priority": int(max_priority),
        "include_categories": selected_categories,
        "include_pets": selected_pets,
    }

    schedule = owner.scheduler.optimize_schedule(constraints)
    warnings = owner.scheduler.get_warnings()

    if schedule:
        st.success("Schedule generated and sorted by scheduler priority/time rules.")
        st.table(schedule)
        total_minutes = sum(item["duration"] for item in schedule)
        st.caption(
            f"Scheduled {len(schedule)} task(s), totaling {total_minutes:.0f} minute(s)."
        )
    else:
        st.info("No tasks matched the selected filters or available time limit.")

    if warnings:
        st.markdown("### Conflict and validation warnings")
        for warning in warnings:
            st.warning(warning)

    st.markdown("### Why this plan?")
    st.text(owner.scheduler.explain_reasoning())
