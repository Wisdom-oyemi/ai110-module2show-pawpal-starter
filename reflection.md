# PawPal+ Project Reflection

## 1. System Design

Basic responsibilities: add pets, schedule walk sessions, view daily tasks, track routines, etc.

**a. Initial design**

- Briefly describe your initial UML design.
Owner is the most important class, because every other class derives from its functionality. The Owner can directly affect the Pet class (via manual manipulation) or through the Scheduler class, which performs actions on the Pet and Task classes automatically.

- What classes did you include, and what responsibilities did you assign to each?
Classes: Owner, Pet, Scheduler, Task

Responsibilities: get assigned tasks/special needs (Pet); assign objective with time duration/priority (Task); add pet/task/schedule (Owner); generate and optimize schedules (Scheduler)

**b. Design changes**

- Did your design change during implementation?
The design changes were minimal, but a few small things were added.

- If yes, describe at least one change and why you made it.
One change that was made was a better link between Pet and Task via implementing a tasks list (for the get_assigned_tasks function to have data to work with).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The Scheduler class considers time and priority as its main constraints.

- How did you decide which constraints mattered most?
These constraints mattered the most because they came directly assigned from the Owner class and therefore had the most influence over the programs development.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My updated scheduler trades an embedded check condition for the HH:MM format with the use of a constantly updating variable that allows for the format to be parsed once per task.

- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable for this scenario because it simplifies the schedule optimization module by introducing reoccurring logic that doesn't get bogged down by nested loops.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Github Copilot mainly for the design brainstorming and refactoring.

- What kinds of prompts or questions were most helpful?
The prompts that were the most helpful were prompts that guided it to image/create situations based on specific guardrails.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I was reconfiguring the optimize_schedule method to add extra task filtering and it wanted to update the test_pawpal.py file instead of the main.py file for input checking.

- How did you evaluate or verify what the AI suggested?
I double-checked which files it wanted to update, read through the code it wanted to implement, and redirected the change.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested mostly task inversion and conflict behaviors, to see if the system would raise warnings as a result of incompatible time slots.

- Why were these tests important?
These tests are important because the scheduler's optimization logic is the lifeblood of the entire program, and it should be able to raise errors in case there are invalid inputs.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am 90% confident my scheduler works correctly.

- What edge cases would you test next if you had more time?
Extended time length conflicts (up to a month or several months)
Misspellings in terms of pet names or preferences

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the improvements made to both the backend logic and the specifically designed test suite.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would probably spend more time redesigning the UI so that it looks less default and more intuitive/on-brand for a pet care system.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that AI can be very efficient with the right guardrails in place, but it may need some encouraging to stay within those guardrails.
