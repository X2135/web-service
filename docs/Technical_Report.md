# Technical Report

## Project Title
Habit & Productivity Analytics API

## Section 1. Introduction and Project Overview

The Habit & Productivity Analytics API is a data-driven REST API project designed to demonstrate how raw behavioral data can be transformed into structured and testable software outputs. The project is based on a 90-day habit tracking dataset, which contains daily records of activities such as workout duration and productivity-related behaviors. This type of dataset was chosen because it includes both structured fields and noisy real-world values, making it suitable for demonstrating practical data cleaning and mapping decisions.

The goal of this project goes beyond implementing basic CRUD functionality. Instead, it focuses on building a complete workflow from data ingestion to API consumption. Raw CSV data is first cleaned and mapped into a relational schema, then exposed through validated REST endpoints. On top of this, an analytics endpoint aggregates key metrics, and a frontend dashboard consumes these API responses for demonstration.

The final system includes a FastAPI backend with full CRUD support for categories and records, an analytics summary endpoint, a pytest-based test suite with 22 passing tests, and a browser-based dashboard. Together, these components form a complete and demonstrable coursework solution.
## Section 2. System Architecture and Technology Choices

The system follows a layered architecture that separates responsibilities across different components. The routing layer defines API endpoints and handles incoming HTTP requests. The CRUD layer contains database interaction logic, including standard create, read, update, and delete operations, as well as analytics aggregation. Schema models are used to validate request and response data, while ORM models define the underlying database structure. The database layer manages connection configuration and session lifecycle.

A typical request flow is: client request → route handler → schema validation → CRUD operation → database read/write → JSON response. This structure ensures that invalid inputs are rejected early, and that business logic remains coherent and centralized. The frontend dashboard acts as an API consumer by calling authentication, CRUD, and analytics endpoints, and rendering the results directly from backend responses.

The technology stack was selected to match the requirements of a coursework-level API system. FastAPI enables rapid development and provides built-in interactive documentation. SQLAlchemy combined with SQLite offers a simple but structured persistence layer suitable for local deployment. Pydantic ensures strict validation of inputs and outputs, reducing runtime errors. Pandas is used for CSV parsing and preprocessing, and Pytest is used to validate system behavior through repeatable test cases. These choices support a system that is stable, testable, and straightforward to understand.
## Section 3. Data Source, Schema Mapping, and Import Pipeline

The project uses a publicly available Kaggle 90-day habit tracker dataset as its primary data source. The dataset is provided in CSV format and contains daily activity records. These raw records are not directly used in the API; instead, they are processed through a custom import pipeline and stored in a relational database.

The data is mapped into two main entities: habit_categories and habit_records. The categories table stores general classifications such as fitness or wellness, while the records table stores daily entries including date, habit name, category reference, completion status, duration, and notes. For example, raw date fields are converted into record_date, and duration-related fields are standardized into duration_minutes.

A key part of this process is rule-based transformation. Categories are inferred from activity patterns in the dataset, and habit_name is generated based on the dominant activity signal rather than fixed labels. The completed field is derived using transparent rules, such as duration thresholds and supporting indicators, which makes the logic easier to explain during evaluation.

The pipeline also performs basic data cleaning, including handling missing values, filtering invalid entries, and avoiding duplicate records. This step is important because the correctness of API responses and analytics results depends on having a clean and well-structured dataset. As a result, the import process forms the foundation of the project’s data-driven design.

## Section 4. API Design, CRUD Functionality, and Analytics

The API is designed around two core resources: `habit_categories` and `habit_records`. Each resource supports full CRUD operations, which satisfies the coursework requirement of providing at least one fully functional CRUD-based data model linked to a relational database. Categories store grouping metadata (name and description), while records store daily observations linked to a category through a foreign key.

The endpoint behavior follows standard REST semantics. `GET` endpoints return lists or single resources, `POST` creates new resources and returns creation responses, `PUT` updates existing resources, and `DELETE` removes resources with predictable status behavior (including 204 for successful deletion). This approach gives clients stable expectations across all endpoints. Responses are JSON-based and follow uniform structures, which improves readability and frontend integration.

Beyond basic CRUD, the API provides a real aggregation endpoint: `/analytics/summary`. This endpoint returns six metrics derived from stored records: `total_records`, `completed_records`, `completion_rate`, `average_duration`, `records_per_category`, and `daily_trend`. These values are computed from persisted database data, confirming that analytics results are derived from actual records rather than hardcoded values or client-side approximations.

The dashboard directly consumes `/analytics/summary` during initial load and refresh actions. As a result, the UI reflects backend analytics output in real time, demonstrating that the project is not only a CRUD service but also a data-driven analytics API with an integrated presentation layer.

## Section 5. Authentication, Error Handling, and Validation

Authentication is implemented using a JWT-based flow. A client first submits credentials to `/auth/login`; if authentication succeeds, the API returns a bearer token. Protected operations then include this token in the `Authorization: Bearer <token>` header. In this project, write operations on categories and records (`POST`, `PUT`, and `DELETE`) are protected, while read operations remain accessible for demonstration and analysis use cases. This design reflects a simplified but appropriate security model for coursework demonstration, balancing protection with practical usability.

Error handling is standardized to improve predictability. Business-rule or invalid-reference issues are returned as `400`, authentication failures or invalid tokens are returned as `401`, and missing resources are returned as `404`. The API uses a standardized error response format containing `detail` and `code`, so clients can parse both human-readable messages and machine-friendly identifiers.

Input validation is enforced through Pydantic schemas. Constraints such as required fields, minimum lengths, and numeric bounds are checked before business logic execution. This prevents malformed payloads from propagating into the data layer and reduces avoidable runtime failures.

Together, JWT enforcement, structured error responses, and schema validation improve API correctness, simplify frontend handling, and make debugging more efficient. For coursework evaluation, this demonstrates deliberate engineering choices rather than ad hoc error handling.

## Section 6. Testing and Validation

Testing is implemented at the API level using Pytest and FastAPI’s TestClient. These tests were designed to cover both expected use cases and failure scenarios, ensuring that API behavior remains stable under different conditions. Current results show that all 22 tests passed successfully, providing measurable evidence that the main API features behave predictably across both normal and failure scenarios.

The suite includes authentication success and failure checks, unauthorized access attempts to protected endpoints, and standard CRUD flows for categories and records. It also verifies key edge and error scenarios: duplicate category creation (`400`), record creation with invalid `category_id` (`400`), and retrieval/deletion of non-existent resources (`404`). In addition, analytics coverage ensures `/analytics/summary` returns expected aggregated fields and values. Boundary validation tests check schema-level constraints for invalid payload inputs.

Validation was not limited to automated tests. Runtime checks were also performed using helper scripts and manual API calls during development to confirm endpoint behavior under interactive conditions. This includes database verification scripts and targeted API check scripts used to cross-check responses outside the test runner.

In this project, testing is treated as evidence of system behavior, not as a formal checkbox. The combination of repeatable automated tests and manual verification supports stronger confidence in correctness, improves maintainability, and provides concrete material for oral defense discussion. The passing test results provide measurable evidence that the system behaves as intended, which is particularly important for both coursework assessment and oral examination.

## Section 7. Challenges and Lessons Learned

One of the main challenges was the quality of the CSV source data. The dataset was not designed to match the database schema directly, so fields had to be mapped carefully before insertion. Some columns were missing in certain rows, while others needed cleaning or type conversion. This made the import process more than a simple file load; it required explicit decisions about which values should be preserved, normalized, or skipped. The lesson here was that data-driven APIs depend heavily on the quality of the transformation layer, not only on the endpoint layer.

Another important design decision was how to infer `completed`. A strict rule based only on duration would have been simple, but it would not have reflected the mixed nature of the dataset. I therefore used a rule-based approach that combined duration and supporting activity signals. This approach was more transparent, but it also involved trade-offs between accuracy and explainability. A similar trade-off appeared when aligning frontend analytics with backend aggregation. Initially, calculating metrics in the browser seemed convenient, but it would have weakened the overall API design. Moving analytics to the backend improved data integrity and made the dashboard a proper consumer of API output. Overall, this experience showed that effective API design requires making clear, justifiable choices when working with imperfect and real-world data.

## Section 8. Limitations and Future Improvements

The current system has several limitations that should be acknowledged. First, authentication is suitable for coursework demonstration, but it is still demo-level rather than production-ready. User management is minimal, credentials are fixed for the demo, and there is no role-based access control. Second, the analytics endpoint is intentionally basic. It provides useful summary metrics, but it does not yet support deeper trend analysis, filtering by date range, or comparative reporting. Third, SQLite is appropriate for local development and testing, but it is not ideal for high-concurrency or larger-scale deployment.

Future improvements would focus on making the system more realistic and scalable. A more complete user system could include registration, hashed passwords, token expiry management, and role-based permissions. The analytics layer could be extended with richer visual summaries, date-based filtering, and category comparisons over time. On the deployment side, the project could be moved from a local SQLite setup to a hosted relational database with proper environment configuration, logging, and CI/CD support. These improvements would strengthen both the technical depth and the professional quality of the system, but they were intentionally left out to keep the coursework implementation clear and manageable.

## Section 9. GenAI Declaration and Reflection

GenAI tools were used as a supporting aid during the project, but not as a replacement for technical judgement. They were helpful in four main areas: ideation, debugging, code suggestion, and documentation drafting. For example, GenAI was used to explore possible analytics metrics, clarify implementation options, and improve the readability of documentation drafts. It also helped identify likely causes of errors during development and suggested refactoring ideas that were later checked manually.

However, all important decisions were made by me. This includes the schema design, the mapping rules for imported data, the authentication approach, the API structure, and the validation strategy. Any generated suggestion was reviewed against the actual codebase and verified through test execution. The final implementation was only accepted after it passed the test suite and matched the expected behavior of the application.

My view is that GenAI is useful when it supports reasoning, but it does not replace it. In this project, it was used to accelerate exploration and improve clarity, while human judgement remained responsible for correctness, coherence, and final acceptance. That distinction is important for coursework integrity and for explaining the work honestly during oral assessment. Examples of GenAI interaction logs are provided as supplementary material to support this declaration, in line with the coursework requirements.
