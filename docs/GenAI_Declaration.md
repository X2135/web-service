# GenAI Declaration and Conversation Logs

## 1. GenAI Declaration

For the project *Habit & Productivity Analytics API*, GenAI tools (including ChatGPT and GitHub Copilot) were used as development support tools rather than as substitutes for independent implementation.

### Why GenAI Was Used

GenAI was used to improve development efficiency in the following areas:
- ideation and exploration of alternative implementation approaches;
- debugging support when diagnosing API behavior and error scenarios;
- code refinement suggestions for improving structure and readability;
- documentation drafting support for README, technical report, and API documentation.

### Where GenAI Was Used

GenAI-assisted discussion and drafting were applied to:
- backend design discussion;
- CRUD and API logic refinement;
- error handling design;
- test case planning;
- documentation writing and formatting.

### Human Responsibility and Final Decisions

All key technical decisions were made by me. Specifically:
- the schema design was defined and finalized by me;
- the CSV-to-database mapping rules were designed by me;
- authentication scope and API structure were determined by me;
- all generated suggestions were reviewed, tested, and selectively integrated by me;
- only code that passed validation checks was accepted.

### Verification and Validation Process

GenAI-generated suggestions were never accepted without verification. Validation included:
- automated test execution using pytest (**22 tests passed**);
- manual API validation through Swagger UI and project scripts;
- direct checking of endpoint responses against expected behavior.

### Academic Integrity Statement

GenAI was used as an assistive tool and not as a substitute for independent work. I take full responsibility for all submitted code and documentation. The final deliverables reflect my own understanding, review, modification, and validation, in line with coursework academic integrity requirements.

---

## 2. Curated Conversation Log Summaries

Selected interaction summaries are included here to reflect the nature of GenAI-assisted development. Full raw conversation logs are not attached; however, the documented summaries capture representative interactions between the user and GenAI tools.

### Example Interaction 1 – API Design

**User Prompt:**  
"How should I structure CRUD endpoints for habit categories and records?"

**AI Response Summary:**  
The AI suggested a resource-oriented REST structure with clear route grouping, status-code semantics, and separation between route handlers, schemas, and CRUD/data-access logic.

**My Decision / Action:**  
I adopted a layered architecture and implemented full CRUD for both `habit_categories` and `habit_records`, then aligned response behavior and status codes with the implemented FastAPI routes.

---

### Example Interaction 2 – Data Import Logic

**User Prompt:**  
"How can I map CSV habit data into a relational schema?"

**AI Response Summary:**  
The AI proposed general mapping strategies, including normalization, handling missing values, and rule-based transformation from raw fields to structured entities.

**My Decision / Action:**  
I defined the actual CSV-to-DB mapping rules myself, including category inference, habit naming, and completion logic, and integrated these rules into the project import pipeline.

---

### Example Interaction 3 – Authentication Design

**User Prompt:**  
"How can I implement JWT authentication in FastAPI?"

**AI Response Summary:**  
The AI provided a standard JWT flow (login endpoint, token generation, bearer-token dependency, and protected route patterns).

**My Decision / Action:**  
I implemented JWT authentication and deliberately restricted protection to write operations (POST/PUT/DELETE) while keeping read endpoints open for coursework demonstration.

---

### Example Interaction 4 – Testing Strategy

**User Prompt:**  
"What test cases should I include for API validation?"

**AI Response Summary:**  
The AI suggested covering success and failure flows, auth checks, invalid inputs, not-found cases, and endpoint-level behavior verification.

**My Decision / Action:**  
I selected and implemented the final test set in pytest, including CRUD, auth, validation boundaries, error paths, and analytics checks, resulting in **22 passed tests**.

---

### Example Interaction 5 – Documentation Writing

**User Prompt:**  
"Help me structure my technical report and API documentation."

**AI Response Summary:**  
The AI suggested formal document structures, section hierarchy, and concise submission-oriented wording suitable for coursework output.

**My Decision / Action:**  
I finalized document content and formatting myself, revised wording for accuracy against the codebase, and prepared submission-ready technical report and API documentation.

---

## 3. Concluding Statement

GenAI significantly improved development speed and drafting efficiency during this project. However, core design decisions, implementation choices, and validation activities remained my responsibility throughout. The final outcome represents human-led development supported by AI assistance, with all final decisions, validation, and submission responsibility retained by the student.
