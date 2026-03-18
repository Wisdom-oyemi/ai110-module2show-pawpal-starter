from pawpal_system import Pet, Task, Owner, Scheduler


def main() -> None:
	owner = Owner(
		name="Jordan",
		email="jordan@example.com",
		available_time_per_day=90,
		preferences={"task_order": "priority_first"},
	)

	pet1 = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
	pet2 = Pet(name="Luna", species="cat", breed="Siamese", age=2)

	owner.add_pet(pet1)
	owner.add_pet(pet2)

	
	task3 = Task(name="Play Session", category="enrichment", duration=20, priority=2, pet=pet2)
	task3 = Task(name="Morning Walk", category="exercise", duration=25, priority=1, pet=pet1)
	task2 = Task(name="Medication", category="health", duration=10, priority=1, pet=pet1)
	

	owner.add_task(task3)
	owner.add_task(task2)
	owner.add_task(task3)

	owner.scheduler = Scheduler(owner)
	schedule = owner.get_schedule()
	warnings = owner.scheduler.get_warnings() if owner.scheduler else []

	print("Today's Schedule")
	print("-" * 40)
	if warnings:
		print("Warnings:")
		for warning in warnings:
			print(f"- {warning}")
		print("-" * 40)

	if not schedule:
		print("No tasks could be scheduled today.")
		return

	for idx, item in enumerate(schedule, start=1):
		pet_name = item["pet"] if item["pet"] else "Unassigned"
		print(
			f"{idx}. {item['task']} ({pet_name}) | "
			f"{item['duration']} min | "
			f"Priority {item['priority']} | "
			f"{item['start_minute']}->{item['end_minute']} min"
		)


if __name__ == "__main__":
	main()

