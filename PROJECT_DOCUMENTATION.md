# AI Data Analyst --- Detailed Project Documentation

**Project type:** Natural-language analytics / Text-to-SQL\
**Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL\
**LLM integration:** Groq through LangChain\
**Frontend:** React 19 and Vite\
**Primary goal:** Let users ask business questions in plain English and
receive database-backed answers without writing SQL.

> **Documentation scope:** This document is based on the supplied
> `ai-data-analyst` project archive and the implementation/debugging
> history available for this project. It distinguishes implemented
> behavior from known limitations and planned improvements. Credentials
> and secret values are intentionally not reproduced.

------------------------------------------------------------------------

## 1. Project Overview

AI Data Analyst converts a natural-language question into a structured
interpretation, resolves ambiguity when necessary, generates a read-only
PostgreSQL query, validates it, executes it, and returns a
human-readable answer together with the result rows and generated SQL.

Example question:

> Which customer spent the most money in Kolkata?

The system should identify: - **Intent:** `identify_top_customer` -
**Metric:** `total_spending` - **Filter:** `city = Kolkata`

The LLM is responsible for interpreting the request and proposing SQL.
PostgreSQL remains the source of truth for business data and
calculations. The application validates generated SQL before execution.

### Project objectives

1.  Make database analysis accessible to users who do not know SQL.
2.  Detect ambiguity rather than silently guessing the user's meaning.
3.  Keep business intent, metric, and filters separate.
4.  Use the live database schema as context for SQL generation.
5.  Restrict generated queries to read-only analysis.
6.  Return both an understandable answer and inspectable query results.
7.  Separate frontend, API, business orchestration, SQL execution, and
    database responsibilities.

------------------------------------------------------------------------

## 2. Features and Current Scope

### Implemented in the supplied code

-   FastAPI application with `/` and `/health` routes.
-   `POST /analyze` endpoint.
-   Pydantic request and response models.
-   PostgreSQL connection through SQLAlchemy and Psycopg 3.
-   Runtime schema inspection using SQLAlchemy's inspector.
-   LLM-based intent analysis using `ChatGroq`.
-   Structured intent output using Pydantic models.
-   Dynamic intent naming rather than a hard-coded intent enum.
-   Extraction of explicit metrics and filters.
-   Ambiguity detection and clarification options.
-   Intent resolution after a user selects a clarification option.
-   LLM-based PostgreSQL query generation.
-   SQL syntax, table, column, and read-only validation.
-   Support for Common Table Expressions (CTEs) in the SQL validation
    path.
-   SQL execution and conversion of returned rows into dictionaries.
-   Human-readable answer formatting.
-   API-level handling for invalid input/clarification, AI-service
    failures, and database failures.
-   React interface for asking questions, choosing suggestions, viewing
    results, inspecting generated SQL, and revisiting recent analyses.
-   Browser-local analysis history using `localStorage`.
-   Unit and API tests; several LLM unit tests use mocks.

### Not to be represented as complete without further verification

-   Full production security for arbitrary generated SQL.
-   Comprehensive coverage for every possible business question or
    database schema.
-   Reliable operation when Groq quota is exhausted.
-   Persistent, server-side user history or multi-user accounts.
-   Authentication, authorization, and tenant isolation.
-   Production observability, rate limiting, and comprehensive
    deployment automation.
-   Fully deterministic SQL generation for all natural-language inputs.

------------------------------------------------------------------------

## 3. Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  Frontend                React 19                Query interface,
                                                  clarification choices,
                                                  results, SQL display,
                                                  local history

  Frontend tooling        Vite                    Development server and
                                                  production build

  API                     FastAPI                 HTTP endpoints, request
                                                  validation, dependency
                                                  injection, error
                                                  responses

  Data validation         Pydantic                Validates request,
                                                  intent, clarification,
                                                  and SQL-generation
                                                  structures

  LLM orchestration       LangChain               Prompt templates and
                                                  structured model
                                                  invocation

  LLM provider            Groq `ChatGroq`         Intent interpretation
                                                  and SQL generation

  Database access         SQLAlchemy              Engine, sessions,
                                                  schema inspection, SQL
                                                  execution

  PostgreSQL driver       Psycopg 3               Python-to-PostgreSQL
                                                  connectivity

  Database                PostgreSQL              Source of truth for
                                                  customers, products,
                                                  orders, and order items

  SQL parsing             SQLGlot (listed in      SQL syntax parsing and
                          requirements and used   validation support
                          in the supplied         
                          validator)              

  Testing                 pytest, FastAPI         Unit and API tests;
                          TestClient,             mocks for isolating LLM
                          unittest.mock           behavior
  -----------------------------------------------------------------------

The supplied `requirements.txt` contains pinned Python dependencies. The
frontend dependencies and scripts are defined in
`frontend/package.json`.

------------------------------------------------------------------------

## 4. High-Level Architecture

``` text
React frontend
    |
    | POST /analyze
    v
FastAPI API layer
    |
    v
AnalysisOrchestrator
    |
    +--> Schema Inspector --------> PostgreSQL metadata
    |
    +--> IntentService -----------> Groq LLM
    |       |
    |       v
    |   IntentAnalysis
    |       |
    |       +--> Ambiguous? ------> Return clarification question/options
    |       |
    |       +--> Resolved request
    |                 |
    |                 v
    +----------> IntentResolutionService
                      |
                      v
                 ResolvedIntent
                      |
                      v
                 AnalysisService
                      |
                      v
                  SQLPipeline
                      |
                      +--> SQLGenerator --> Groq LLM
                      |
                      +--> SQLValidator
                      |
                      v
                  SQLExecutor -----------> PostgreSQL data
                      |
                      v
                  AnswerFormatter
                      |
                      v
           JSON response: answer, rows, SQL
                      |
                      v
                 React results UI
```

### Responsibility boundaries

-   **IntentService:** understands the question. It does not execute
    SQL.
-   **ClarificationService:** exposes clarification options supplied by
    intent analysis.
-   **IntentResolutionService:** validates a selected option and creates
    `ResolvedIntent`.
-   **SQLGenerator:** generates a query and a brief explanation using
    the resolved intent and schema.
-   **SQLValidator:** rejects unsupported or unsafe SQL patterns and
    checks referenced schema objects.
-   **SQLExecutor:** executes the validated query using the request's
    database session.
-   **AnswerFormatter:** converts returned rows into readable text.
-   **AnalysisOrchestrator:** coordinates the full flow and returns
    either a clarification response or a completed result.

This separation makes components easier to test and reduces the risk of
mixing interpretation, query generation, execution, and presentation
logic.

------------------------------------------------------------------------

## 5. Database Design

The supplied schema is in `backend/db/schema.sql`. It defines four
tables.

### 5.1 `customers`

  -----------------------------------------------------------------------
  Column                  Type                    Meaning
  ----------------------- ----------------------- -----------------------
  `id`                    SERIAL, primary key     Customer identifier

  `name`                  VARCHAR(100), required  Customer name

  `email`                 VARCHAR(150), unique    Customer email
                          and required            

  `city`                  VARCHAR(100)            Customer city

  `created_at`            TIMESTAMP               Creation timestamp,
                                                  defaults to current
                                                  time
  -----------------------------------------------------------------------

### 5.2 `products`

  Column       Type                      Meaning
  ------------ ------------------------- --------------------
  `id`         SERIAL, primary key       Product identifier
  `name`       VARCHAR(150), required    Product name
  `category`   VARCHAR(100)              Product category
  `price`      NUMERIC(10,2), required   Product price

### 5.3 `orders`

  Column          Type                   Meaning
  --------------- ---------------------- ---------------------------------------
  `id`            SERIAL, primary key    Order identifier
  `customer_id`   INTEGER, foreign key   References `customers.id`
  `order_date`    TIMESTAMP              Order timestamp
  `status`        VARCHAR(50)            Order status; defaults to `completed`

### 5.4 `order_items`

  -----------------------------------------------------------------------
  Column                  Type                    Meaning
  ----------------------- ----------------------- -----------------------
  `id`                    SERIAL, primary key     Order-item identifier

  `order_id`              INTEGER, foreign key    References `orders.id`

  `product_id`            INTEGER, foreign key    References
                                                  `products.id`

  `quantity`              INTEGER, required       Units in this line item

  `unit_price`            NUMERIC(10,2), required Unit price recorded for
                                                  this line item
  -----------------------------------------------------------------------

### Relationships

``` text
customers 1 ---- many orders
orders    1 ---- many order_items
products  1 ---- many order_items
```

### Important business calculations

-   **Line-item amount:** `quantity * unit_price`
-   **Order total:** sum of line-item amounts for an order
-   **Customer spending/revenue:** aggregate relevant order-item
    amounts, applying the appropriate order-status rule
-   **Average order value per customer:** calculate each order's total
    first, then average those order totals for that customer
-   **Order count:** count the relevant orders, not the joined
    order-item rows

The SQL-generation prompt explicitly tells the model to use completed
orders for relevant spending/revenue calculations and to avoid joins
that multiply aggregate totals. These are prompt-level business rules
and should also be verified through regression tests.

------------------------------------------------------------------------

## 6. Intent Model: Intent, Metric, and Filters

A key design decision is to avoid creating a separate intent for every
combination of operation, metric, and filter.

### Intent

Describes **what operation** the user wants.

Examples: - `identify_top_customer` - `calculate_total_revenue` -
`filter_customers` - `identify_top_selling_product` -
`calculate_revenue_by_month`

These are examples, not an exhaustive enum.

### Metric

Describes **how a result should be measured or ranked**.

Examples: - `total_spending` - `order_count` - `average_order_value` -
`total_revenue` - `lifetime_value`

### Filters

Describe **which subset of data** should be analyzed.

Example:

``` json
{
  "city": "Kolkata"
}
```

This separation avoids brittle intent names such as
`identify_top_customer_in_kolkata`. The city belongs in the filters, not
in the intent name.

### Structured models

`backend/app/models/intent.py` defines: - `ClarificationOption` -
`IntentAnalysis` - `ResolvedIntent` - `SQLGenerationResult`

Pydantic structures help ensure the LLM response has the expected fields
before application code uses it.

------------------------------------------------------------------------

## 7. Clarification Engine

The system should ask a question when the user's request has multiple
reasonable interpretations.

Example:

**User:** "Who is the best customer?"

"Best" does not specify a metric. Possible interpretations in the
current prompt include: - highest total spending - highest number of
orders - highest average order value - highest lifetime value

The expected first response has: - `status = "clarification_required"` -
no final answer - a clarification question - a list of selectable
options - no generated SQL

After the user chooses an option, the frontend sends the original
question plus `selected_option` to `POST /analyze`. The backend analyzes
the question again, validates the selected value against the returned
option values, resolves the intent, and proceeds to SQL generation.

### Current implementation consideration

The supplied API sends the original question and selected option in a
second request; it does not show a server-side persisted clarification
session. Therefore, the intent analysis is performed again rather than
being retrieved from a stored conversation record. For a production
system, consider returning a short-lived clarification/session
identifier and storing the original analysis server-side, or carefully
verifying the selected option against a fresh analysis as the current
implementation does.

------------------------------------------------------------------------

## 8. End-to-End Request Lifecycle

Consider this question:

> Which customer spent the most money in Kolkata?

### Step 1: Frontend request

The React application sends JSON to `POST /analyze`:

``` json
{
  "question": "Which customer spent the most money in Kolkata?",
  "selected_option": null
}
```

### Step 2: Request validation

FastAPI validates the request against `AnalysisRequest`. The question
must contain at least one character after the model's basic length
validation. The frontend also trims whitespace before sending it.

### Step 3: Schema inspection

`get_database_schema()` inspects the connected PostgreSQL database to
obtain table names, columns, data types, nullability, and foreign-key
information. This supplies structural context; it does not load every
business row into the prompt.

### Step 4: Intent analysis

`IntentService` uses `ChatGroq` with the `openai/gpt-oss-120b` model
name and temperature 0. The prompt asks the LLM to return structured
`IntentAnalysis` data and not to generate or execute SQL at this stage.

Expected interpretation:

``` json
{
  "intent": "identify_top_customer",
  "ambiguous": false,
  "metric": "total_spending",
  "filters": {
    "city": "Kolkata"
  }
}
```

The exact model response can vary; the JSON above illustrates the
intended contract.

### Step 5: Resolution

The orchestrator passes the analysis through `IntentResolutionService`
to produce a `ResolvedIntent`. When the request is not ambiguous, the
current code uses the analysis's intent, metric, and filters directly.

### Step 6: SQL generation

`SQLPipeline` obtains the schema and calls `SQLGenerator`. The
generator's prompt requires one read-only PostgreSQL query and tells the
LLM to use only supplied schema objects, preserve filters and metrics,
and follow the documented calculation rules.

A representative query might look like this:

``` sql
SELECT
    c.id,
    c.name,
    SUM(oi.quantity * oi.unit_price) AS total_spending
FROM customers AS c
JOIN orders AS o
    ON c.id = o.customer_id
JOIN order_items AS oi
    ON o.id = oi.order_id
WHERE c.city = 'Kolkata'
  AND o.status = 'completed'
GROUP BY c.id, c.name
ORDER BY total_spending DESC
LIMIT 1;
```

This is an illustrative query, not a guarantee of the exact SQL
generated for every request.

### Step 7: SQL validation

The validator checks the query before it reaches the database. The
supplied implementation uses SQLGlot for syntax parsing and also
validates query type, forbidden operations, tables, aliases, and
columns, including CTE references.

### Step 8: SQL execution

`SQLExecutor` calls SQLAlchemy's `db.execute(text(sql))`, fetches
mapping rows, and converts each result to a Python dictionary.
PostgreSQL performs the actual filtering, joins, grouping, and
aggregation.

### Step 9: Answer formatting

`AnswerFormatter` checks whether rows were returned and formats results
according to the resolved intent and metric. It also has generic
row-formatting behavior for result sets that do not match a specialized
formatter.

### Step 10: Response to frontend

The completed response includes status, readable answer, SQL, and rows.
The React UI renders the answer and a results table and allows the user
to reveal the generated SQL.

------------------------------------------------------------------------

## 9. API Reference

### `GET /`

Purpose: basic application liveness check.

Example response:

``` json
{
  "message": "AI Data Analyst API is running"
}
```

### `GET /health`

Purpose: checks whether a database query can be executed.

Example response:

``` json
{
  "status": "healthy",
  "database": "connected"
}
```

This is a basic connectivity check, not a comprehensive readiness or
dependency health report.

### `POST /analyze`

Purpose: analyze a natural-language question.

Request model:

``` json
{
  "question": "What is our total revenue?",
  "selected_option": null
}
```

`selected_option` is optional and is used when answering a clarification
question.

#### Completed response shape

``` json
{
  "status": "completed",
  "answer": "The total revenue is ...",
  "clarification_question": null,
  "clarification_options": [],
  "sql": "SELECT ...",
  "rows": [
    {
      "total_revenue": 440500
    }
  ]
}
```

The amount above is an example of the response shape, not a promise that
a fresh database has that value. Actual values depend on the current
database contents and seed data.

#### Clarification response shape

``` json
{
  "status": "clarification_required",
  "answer": null,
  "clarification_question": "How should the best customer be determined?",
  "clarification_options": [
    {
      "value": "total_spending",
      "label": "Highest total spending"
    },
    {
      "value": "order_count",
      "label": "Highest number of orders"
    }
  ],
  "sql": null,
  "rows": []
}
```

The actual options are supplied by the intent-analysis model and may
include more choices.

#### Error behavior

The supplied route maps: - `ValueError` to HTTP 400 - Groq `APIError` to
HTTP 503 with a user-friendly AI-service message - SQLAlchemy errors to
HTTP 503 with a user-friendly database-service message

Other unexpected exceptions may still need a consistent global exception
handler and server-side logging.

------------------------------------------------------------------------

## 10. Backend File Guide

``` text
backend/
├── __init__.py
├── db/
│   ├── schema.sql
│   └── seed.sql
└── app/
    ├── main.py
    ├── api/
    │   └── analysis.py
    ├── db/
    │   └── connection.py
    ├── models/
    │   ├── analysis.py
    │   └── intent.py
    └── services/
        ├── analysis_orchestrator.py
        ├── analysis_service.py
        ├── answer_formatter.py
        ├── clarification_service.py
        ├── intent_resolution_service.py
        ├── intent_service.py
        ├── schema_inspector.py
        ├── sql_executor.py
        ├── sql_generator.py
        ├── sql_pipeline.py
        └── sql_validator.py
```

  -----------------------------------------------------------------------
  File                                Purpose
  ----------------------------------- -----------------------------------
  `main.py`                           Creates FastAPI app, configures
                                      CORS, includes the analysis router,
                                      exposes root and health routes

  `api/analysis.py`                   Defines `POST /analyze`, injects DB
                                      session, maps known errors to HTTP
                                      responses

  `db/connection.py`                  Loads settings, builds SQLAlchemy
                                      URL/engine/session factory, yields
                                      request sessions

  `models/analysis.py`                API request/response schemas

  `models/intent.py`                  Structured intent, clarification,
                                      resolved intent, and SQL generation
                                      models

  `analysis_orchestrator.py`          Coordinates intent analysis,
                                      clarification, resolution, and
                                      analysis execution

  `analysis_service.py`               Coordinates SQL pipeline, executor,
                                      and answer formatter

  `intent_service.py`                 LLM-based natural-language intent
                                      analysis

  `clarification_service.py`          Returns model-supplied
                                      clarification choices for ambiguous
                                      questions

  `intent_resolution_service.py`      Validates selected clarification
                                      options and builds resolved intent

  `schema_inspector.py`               Reads database metadata dynamically

  `sql_generator.py`                  Produces structured SQL and an
                                      explanation via the LLM

  `sql_validator.py`                  Parses and validates generated SQL
                                      before execution

  `sql_executor.py`                   Executes validated SQL and returns
                                      dictionary rows

  `answer_formatter.py`               Converts SQL results into readable
                                      output
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 11. Frontend Overview

The supplied frontend uses React 19 and Vite.

### User-facing behavior visible in the source

-   Natural-language question input.
-   Suggested example questions.
-   Loading state while a question is analyzed.
-   Error display when a request fails.
-   Clarification options for ambiguous questions.
-   Human-readable answer and result rows.
-   Expand/collapse control for generated SQL.
-   Copy-SQL action.
-   Recent analysis history stored in browser `localStorage`.
-   Search over locally saved history.
-   Start-new-analysis flow.

### Frontend API configuration

`frontend/src/App.jsx` reads:

``` js
const API = import.meta.env.VITE_API_BASE_URL
```

The archive contains: - `frontend/.env.development` configured for a
local FastAPI URL. - `frontend/.env.production` configured for a hosted
backend URL.

Do not assume those hosted URLs remain active. Verify deployment
configuration before publishing or changing environments. Vite
environment variables are embedded in the client bundle; they must never
contain database passwords, Groq API keys, or other secrets.

### Vite proxy

`frontend/vite.config.js` defines a development proxy for `/api` to the
local backend and strips the `/api` prefix. The current React code calls
the configured base URL directly, so the proxy is useful only if the
frontend uses the proxy path in the relevant environment.

### Frontend scripts

Run from the `frontend` directory:

``` powershell
npm install
npm run dev
```

Production build:

``` powershell
npm run build
```

Lint:

``` powershell
npm run lint
```

The presence of a build script does not by itself prove that the latest
build or lint run succeeds; run those commands locally before release.

------------------------------------------------------------------------

## 12. Environment Configuration and Local Setup

### Prerequisites

-   Python version compatible with the pinned requirements; the project
    was developed in a Python 3.12 environment.
-   PostgreSQL installed and running.
-   Node.js and npm for the React frontend.
-   A Groq API key with access to the configured model.
-   Git (optional, for version control).

### 12.1 Create the PostgreSQL database

Create a database named `ai_data_analyst` (or use another name and
configure `.env` accordingly).

Using `psql`, for example:

``` sql
CREATE DATABASE ai_data_analyst;
```

Connect to that database, then run the schema and seed scripts from the
project root:

``` powershell
psql -U postgres -d ai_data_analyst -f backend/db/schema.sql
psql -U postgres -d ai_data_analyst -f backend/db/seed.sql
```

If your PostgreSQL username or database name differs, adjust the
command. Avoid rerunning `schema.sql` against a database where the
tables already exist unless you have intentionally reset the schema.

### 12.2 Create a Python virtual environment

From the project root:

``` powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use the appropriate local
execution-policy guidance for your machine rather than disabling
security controls globally.

### 12.3 Configure `.env`

Create a root `.env` file. Use placeholder values first, then fill them
in locally:

``` dotenv
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=replace_with_your_local_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ai_data_analyst
DATABASE_SSLMODE=disable
GROQ_API_KEY=replace_with_your_groq_api_key
```

The settings model uses Pydantic Settings and reads `.env`.
`URL.create()` is used to construct the SQLAlchemy URL safely, including
when a database password contains special characters such as `@`.

Never commit `.env`. Keep `.env.example` limited to placeholder values.

### 12.4 Start the backend

From the project root, with the virtual environment active:

``` powershell
uvicorn backend.app.main:app --reload
```

Open: - `http://127.0.0.1:8000/` - `http://127.0.0.1:8000/health` -
`http://127.0.0.1:8000/docs`

The Swagger UI at `/docs` can be used to submit `POST /analyze`
requests.

### 12.5 Start the frontend

Open a second terminal:

``` powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. Confirm `VITE_API_BASE_URL` points
to the backend you intend to use.

### 12.6 Verify the connection

First call `/health`. If it fails, check: 1. PostgreSQL service is
running. 2. Database exists. 3. Credentials and port are correct. 4.
`DATABASE_SSLMODE` matches the environment. 5. Required tables exist. 6.
Psycopg is installed correctly.

Then submit a simple question through Swagger or the frontend.

------------------------------------------------------------------------

## 13. Testing Strategy

The project uses pytest and FastAPI's `TestClient`. Tests cover database
connectivity, service behavior, intent analysis, clarification, SQL
generation, SQL execution, validation, and API responses.

Run all tests from the project root:

``` powershell
pytest -q
```

Run a focused validator test:

``` powershell
pytest backend\app\services\test_sql_validator.py -q
```

Run API tests:

``` powershell
pytest backend\app\api\test_analysis.py -q
```

### Why mocking matters

Unit tests should not need to call a live Groq endpoint. A test that
depends on an external model can fail because of: - API quota exhaustion
or rate limits, - network failures, - provider downtime, - model
response variation, - additional latency and cost.

The supplied intent-service and SQL-generator unit tests use
`unittest.mock` to replace `ChatGroq` and return known structured
results. Continue applying the same approach to unit tests. Keep
live-provider checks separate and explicitly opt-in.

### Test result reporting

During development, the SQL validator's focused test file was observed
to pass **5 tests** in a run of
`pytest backend\app\services\test_sql_validator.py -q`. In a separate
full-suite run, **8 tests failed and 13 passed** because the live Groq
requests hit HTTP 429 quota/rate-limit errors. Those results refer to
different runs; they should not be combined into one test report. Re-run
the current suite after test isolation changes before claiming the whole
suite passes.

------------------------------------------------------------------------

## 14. Problems Faced and How They Were Addressed

This section records the main debugging lessons from the project's
development history. "Addressed" does not mean the entire project is now
production-ready; the scope of each fix is stated.

### Problem 1: Database passwords containing special characters

**Symptom:** A database URL could break when a password contained
characters such as `@`, because the character can be interpreted as part
of URL syntax.

**Cause:** Building a connection URL through manual string concatenation
requires correct URL escaping.

**Solution:** The connection module uses SQLAlchemy's `URL.create()`
with separate username, password, host, port, and database arguments.
This avoids manually embedding credentials into a URL string.

**Lesson:** Prefer structured URL construction over manual interpolation
for database credentials.

### Problem 2: PostgreSQL driver / Psycopg import errors

**Symptom:** During setup, the project encountered Psycopg errors such
as a missing `pq` wrapper.

**Cause:** The installed Psycopg runtime or binary dependencies were not
available in the environment as expected.

**Resolution approach:** Verify that the intended virtual environment is
active, install the project's declared Psycopg dependencies, and verify
imports and a real database connection before debugging
application-level SQL. The supplied requirements include `psycopg` and
`psycopg-binary`.

**Lesson:** Confirm the Python interpreter and driver installation
first; a driver import problem is different from a SQLAlchemy query bug.

### Problem 3: Python package imports during pytest

**Symptom:** Tests using imports such as `from backend.app...` initially
failed to resolve the package.

**Cause:** The test runner's import path and package layout were not
aligned.

**Solution:** A `backend/__init__.py` package marker is present in the
project, and tests are run from the project root so `backend.app` can be
resolved consistently.

**Lesson:** Run tests from the repository root and keep imports
consistent with the package structure.

### Problem 4: "Best customer" was ambiguous

**Symptom:** The question "Who is the best customer?" does not say
whether "best" means spending, order count, average order value, or
another business metric.

**Cause:** A single vague adjective can represent several valid
analytical operations.

**Solution:** The intent prompt instructs the LLM not to guess when
multiple interpretations are reasonable. It returns a clarification
question and selectable metric options. The intent-resolution service
validates the user's selection before analysis proceeds.

**Lesson:** Ask for clarification when business meaning is
under-specified rather than silently choosing a metric.

### Problem 5: Fixed intent enums would not scale

**Symptom:** A fixed enum requires code changes for every new intent and
can encourage separate intent values for every filter/metric
combination.

**Cause:** Business operations, measures, and filters are different
concepts.

**Solution:** The source enum file was removed from the active source
design. The intent is represented as a string generated from the user's
request, while metric and filters are separate fields in
`IntentAnalysis` and `ResolvedIntent`. Prompt examples are explicitly
described as examples rather than a complete list.

**Lesson:** Keep the semantic model extensible, but validate downstream
SQL and business rules independently. Dynamic intent naming does not
mean generated SQL should be trusted.

### Problem 6: CTE queries were rejected or their columns were not recognized

**Symptom:** SQL using a Common Table Expression, for example
`WITH order_totals AS (...)`, failed validation because the validator
treated the CTE name as an unknown physical table or could not recognize
columns such as `order_total` and `customer_id`.

**Cause:** The initial validator was designed around ordinary `SELECT`
queries and physical table aliases. CTEs introduce temporary named query
results whose columns do not appear in the physical database schema.

**Solution:** The validator was expanded to recognize CTEs, extract
exposed column names, distinguish CTEs from physical tables, and
validate qualified references to CTE aliases. SQLGlot syntax parsing is
also present in the supplied validator. The focused validator suite
subsequently passed 5 tests in a recorded run.

**Limitations:** Regex-based alias/column extraction can be brittle for
complex SQL. SQLGlot provides a stronger parsing foundation, but the
validator still needs adversarial tests for nested/multiple CTEs,
comments, string literals, quoted identifiers, ambiguous columns, and
dialect edge cases.

**Lesson:** A read-only keyword check alone is not a sufficient SQL
security boundary.

### Problem 7: Answer formatting did not match the selected metric

**Symptom:** A query could correctly return a customer ranked by order
count, but the answer formatter might use wording intended for spending
or fall back to a generic row count.

**Cause:** SQL generation and result formatting are separate stages;
each supported metric needs an appropriate presentation rule or safe
generic fallback.

**Solution:** The answer formatter gained metric-aware wording for
supported cases, including the `order_count` result. A regression
assertion was added to the API test for the expected "highest number of
completed orders" wording.

**Lesson:** Test the final user-facing answer, not just whether SQL
contains `COUNT` or whether a query returned rows.

### Problem 8: Groq HTTP 429 errors made the full test run fail

**Symptom:** A full pytest run reported 8 failures and 13 passes. The
failure traces showed Groq HTTP 429 errors caused by request/token quota
limits. The failures occurred in tests that reached the live model
provider.

**Cause:** Tests depended on external LLM calls, so they could fail even
when the application logic under test was not the source of the problem.

**Solution direction:** Mock LLM calls in unit tests and reserve
real-provider calls for a separate opt-in integration test. The supplied
intent and SQL-generator unit tests already demonstrate the mocking
pattern. The entire suite must still be re-run after remaining
API/service tests are isolated.

**Status:** The rate-limit cause was identified. Do not claim the
complete suite is fixed until the full test suite passes without
depending on live Groq calls.

### Problem 9: Distinguishing schema inspection from business-data retrieval

**Question that came up:** How does the application get values from
PostgreSQL?

**Explanation:** `schema_inspector.py` retrieves metadata about tables
and columns. It does not preload all customer/order rows. `SQLExecutor`
executes the validated generated query through the SQLAlchemy session,
fetches rows, and converts them into dictionaries. The database performs
the actual joins and calculations.

**Lesson:** Schema metadata helps the model formulate SQL; the query
execution step retrieves business values.

### Problem 10: Debugging output inside service code

**Symptom:** Temporary `print()` statements were used to inspect
generated SQL and returned rows.

**Risk:** Debug prints can expose business data or query details in logs
and clutter production output.

**Improvement:** Remove temporary prints before committing or deploying.
Replace them with structured, configurable logging that avoids secrets
and sensitive query parameters.

------------------------------------------------------------------------

## 15. Security and Reliability Considerations

Text-to-SQL is powerful, but generated SQL must be treated as untrusted
input even when it comes from a model.

### Controls present in the supplied implementation

-   The SQL generator prompt requests one read-only PostgreSQL query.
-   The validator checks syntax and query type.
-   Forbidden data-modifying keywords are rejected.
-   Table and column references are checked against schema metadata.
-   The API handles known Groq and SQLAlchemy errors with
    service-unavailable responses.
-   Credentials are loaded from environment configuration rather than
    intentionally embedded in source code.

### Additional controls recommended before production

1.  **Use a read-only database role.** Grant only `SELECT` on approved
    schemas/tables. This is a critical defense if application validation
    misses a malicious query.
2.  **Use SQLGlot's parsed AST as the main validation basis.** Avoid
    relying only on regexes to determine query structure.
3.  **Reject multiple statements and non-SELECT AST nodes.** Explicitly
    test `WITH` queries, nested queries, comments, quoted identifiers,
    and database-specific syntax.
4.  **Apply statement timeouts and result limits.** A valid query can
    still be expensive.
5.  **Allowlist accessible schemas and tables.** Do not expose
    internal/system tables to the model unless required.
6.  **Validate filter fields and value handling.** Ensure user-supplied
    values are treated as data and are not allowed to change query
    structure.
7.  **Avoid leaking raw exceptions.** Return safe messages to clients
    and log details securely on the server.
8.  **Add authentication and rate limiting** before exposing the API
    publicly.
9.  **Configure CORS precisely.** The supplied `main.py` contains a
    specific hosted frontend origin. Verify it matches the actual
    frontend origin exactly; browser origins normally do not include a
    trailing slash.
10. **Keep secrets out of frontend variables.** Variables prefixed with
    `VITE_` are available in the browser bundle.
11. **Do not commit `.env`, local caches, `.venv`, `node_modules`, or
    build artifacts** unless a deliberate release process requires a
    specific artifact.
12. **Add observability.** Record request IDs, durations, model
    failures, validation rejections, and database errors without logging
    credentials or sensitive row contents.
13. **Consider whether generated SQL should be returned to every user.**
    It is useful for transparency in this project, but access to SQL may
    need restriction in a multi-user business application.

A prompt is not a security boundary. The database's permissions and the
validator must enforce the actual access policy.

------------------------------------------------------------------------

## 16. Known Limitations and Work Remaining

Based on the supplied code and the development history, the following
work should be prioritized:

### Priority 1 --- Make the full test suite independent of live Groq calls

-   Mock `IntentService` and `SQLGenerator` in unit tests.
-   Mock LLM-dependent collaborators in service/API tests when the test
    is not specifically testing the provider.
-   Add a separate integration marker or environment flag for live Groq
    tests.
-   Verify the full suite passes with the API key unavailable or network
    disabled.

### Priority 2 --- Harden SQL validation

-   Add regression tests for multiple CTEs and nested CTEs.
-   Add tests for DML hidden in CTEs, multiple statements, comments,
    quoted identifiers, unknown aliases, unknown columns, and
    schema-qualified names.
-   Prefer AST validation with SQLGlot and a read-only database role.

### Priority 3 --- Improve exception handling and observability

-   Replace temporary debug prints with structured logging.
-   Add a global handler for unexpected exceptions.
-   Return stable error codes/messages while preserving safe server-side
    diagnostics.
-   Add request timeout and query timeout policies.

### Priority 4 --- Expand and verify supported business questions

-   Revenue by month.
-   Best-selling products.
-   Customer order analysis.
-   Average order value.
-   Comparisons between cities/customers.
-   Empty-result and unsupported-question behavior.
-   Explicit metric/filter validation and business-definition regression
    tests.

A prompt example or test fixture does not by itself prove every listed
operation works end to end against the live database.

### Priority 5 --- Frontend and deployment polish

-   Verify API base URL and CORS configuration for each environment.
-   Test loading, errors, clarification choices, result tables, SQL
    display, and history behavior.
-   Confirm `npm run build` and `npm run lint` pass.
-   Add deployment instructions and environment-specific configuration.
-   Add authentication if the project is exposed beyond a trusted demo
    environment.

### Priority 6 --- Documentation and reproducibility

-   Keep `.env.example` current.
-   Document database reset/seed steps.
-   Include example requests and responses.
-   Record the Python and Node versions actually tested.
-   Keep this document aligned with code changes.

------------------------------------------------------------------------

## 17. Suggested Development Workflow

1.  Create or activate `.venv`.
2.  Confirm `.env` is configured locally and not tracked by Git.
3.  Ensure PostgreSQL is running and `/health` succeeds.
4.  Run focused tests for the component being changed.
5.  Run the full pytest suite after external LLM calls are mocked.
6.  Run frontend lint and production build.
7.  Inspect `git diff` before staging.
8.  Commit one coherent change with a descriptive message.
9.  Push the feature branch and verify the push result.
10. Update this documentation when behavior or setup changes.

Suggested commit message examples:

``` text
docs: add detailed project documentation
test: isolate LLM unit tests from Groq API
fix: strengthen CTE SQL validation
feat: improve clarification experience
```

------------------------------------------------------------------------

## 18. Final Summary

The project has a meaningful end-to-end foundation: a React interface,
FastAPI endpoint, schema-aware LLM workflow, clarification engine, SQL
generation and validation pipeline, PostgreSQL execution, and answer
formatting.

The most important engineering lessons from development are:

-   Separate intent, metric, and filters instead of expanding a fixed
    enum.
-   Ask for clarification when the request is ambiguous.
-   Treat generated SQL as untrusted and validate it before execution.
-   Test CTEs and other SQL structures explicitly.
-   Keep unit tests deterministic by mocking external model calls.
-   Use structured database URL construction for special-character
    passwords.
-   Distinguish infrastructure failures, such as driver issues or rate
    limits, from application logic defects.
-   Report test results accurately and only claim a fix after rerunning
    the relevant tests.

The next milestone should be **a fully isolated, reproducible test
suite**, followed by SQL-validator hardening and end-to-end verification
of the frontend/backend workflow.
