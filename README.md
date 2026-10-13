# AI Data Analyst

An AI-powered data analysis application that lets users ask questions about relational business data in natural language. The backend uses an LLM to interpret the request, asks for clarification when the request is ambiguous, generates PostgreSQL SQL, validates the query, executes it against PostgreSQL, and returns a readable answer alongside the result rows and SQL.

> **Project status:** The core backend workflow and React interface are implemented. This is an actively developed project; review the testing and limitations sections before treating it as production-ready.

## Features

- **Natural-language analysis:** Ask business questions without writing SQL manually.
- **Model-driven intent analysis:** The LLM identifies the requested operation, metric, and explicitly stated filters instead of relying on a fixed intent enum.
- **Clarification flow:** Ambiguous questions can return a clarification question and selectable options before a query is executed.
- **Schema-aware SQL generation:** The generator receives database schema information and creates PostgreSQL queries for the resolved request.
- **Read-only SQL validation:** The validator checks generated SQL before execution and rejects unsupported or dangerous operations.
- **PostgreSQL execution:** SQLAlchemy executes the validated query and returns structured rows.
- **Readable answers and result tables:** The API returns a natural-language answer, generated SQL, and result rows. The React UI can display the tabular results.
- **Analysis history in the browser:** The frontend saves recent successful analyses in browser `localStorage`.
- **Health endpoint:** Check API and database connectivity.

## Architecture

```text
User question
    |
    v
FastAPI POST /analyze
    |
    v
AnalysisOrchestrator
    |
    +--> IntentService (LLM)
    |       - infer business operation
    |       - identify metric and filters
    |       - detect ambiguity
    |
    +--> ClarificationService (if needed)
    |       - return question and options
    |
    +--> IntentResolutionService
    |
    v
AnalysisService
    |
    v
SQLPipeline
    +--> SQLGenerator (LLM + database schema)
    +--> SQLValidator
    |
    v
SQLExecutor --> PostgreSQL
    |
    v
AnswerFormatter
    |
    v
Answer + SQL + result rows --> React UI
```

### Important design separation

- **Intent** describes what business operation the user wants.
- **Metric** describes how the result should be measured or ranked.
- **Filters** specify which subset of data should be analyzed.
- The LLM interprets the request and proposes SQL; application code validates the SQL before execution.
- PostgreSQL remains the source of truth for business records and calculations.

## Technology stack

### Backend

- Python
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy and Psycopg 3
- Pydantic and Pydantic Settings
- LangChain Core and LangChain-Groq
- Groq-hosted `openai/gpt-oss-120b` model (as configured in the services)
- pytest and HTTPX for tests

### Frontend

- React 19
- Vite
- JavaScript and CSS

## Repository structure

```text
ai-data-analyst/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routes and API tests
│   │   ├── db/              # Database connection and connection tests
│   │   ├── models/          # Pydantic request/response and intent models
│   │   ├── services/        # Intent, clarification, SQL, execution, formatting
│   │   └── main.py          # FastAPI application
│   └── db/
│       ├── schema.sql       # Database table definitions
│       └── seed.sql         # Example records
├── frontend/
│   ├── src/                 # React application and styles
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Database schema

The supplied schema defines four related tables:

| Table | Purpose | Key relationships |
|---|---|---|
| `customers` | Customer details, including name, email, and city | Referenced by `orders` |
| `products` | Product names, categories, and prices | Referenced by `order_items` |
| `orders` | Customer orders, dates, and status | References `customers` |
| `order_items` | Products, quantities, and unit prices within orders | References `orders` and `products` |

The schema and example seed data are in `backend/db/schema.sql` and `backend/db/seed.sql`. Revenue and order-item totals should be calculated from `quantity * unit_price`; the SQL generator's prompt also specifies completed-order rules for relevant revenue and customer-ranking operations.

## Prerequisites

Install the following before running the project:

- Python 3.12 (the project was developed with Python 3.12)
- Node.js and npm
- PostgreSQL
- A Groq API key with access to the configured model
- Git (optional, for version control)

## Local setup

The commands below use PowerShell on Windows and assume you are in the repository root.

### 1. Configure environment variables

Create a root `.env` file. Do not commit this file.

```dotenv
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ai_data_analyst
DATABASE_SSLMODE=disable
GROQ_API_KEY=your_groq_api_key
```

These names correspond to the settings used by the backend. Use your own database credentials and API key. `DATABASE_SSLMODE=disable` is suitable only for a local PostgreSQL setup; configure SSL appropriately for a hosted database.

### 2. Create and initialize the PostgreSQL database

Create a database named `ai_data_analyst` in PostgreSQL. Then run the SQL files from the repository root. For example, using `psql`:

```powershell
psql -U postgres -d ai_data_analyst -f backend/db/schema.sql
psql -U postgres -d ai_data_analyst -f backend/db/seed.sql
```

Replace `postgres` with your PostgreSQL username if needed. Run the schema before the seed file. The seed file is example data and should not be applied repeatedly to a database where those records already exist.

### 3. Set up and run the backend

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

The API should be available at `http://127.0.0.1:8000`.

Useful endpoints:

- `GET http://127.0.0.1:8000/` — confirms the API is running.
- `GET http://127.0.0.1:8000/health` — checks database connectivity.
- `POST http://127.0.0.1:8000/analyze` — analyzes a natural-language question.
- `http://127.0.0.1:8000/docs` — interactive Swagger API documentation.

### 4. Set up and run the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create or update `frontend/.env.development` with the local backend URL:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then start Vite:

```powershell
npm run dev
```

Open the local URL printed by Vite in the terminal. The frontend uses `VITE_API_BASE_URL` to call the backend. For production, set this variable to the deployed API's base URL and ensure the backend CORS configuration allows the frontend's exact origin.

## API usage

### Request

`POST /analyze`

```json
{
  "question": "Which customer spent the most money in Kolkata?"
}
```

### Completed analysis response

A successful analysis returns a response shaped like this. Values below are illustrative; actual rows and answers depend on the database contents and generated SQL.

```json
{
  "status": "completed",
  "answer": "The highest-spending customer is ...",
  "clarification_question": null,
  "clarification_options": [],
  "sql": "SELECT ...",
  "rows": [
    {
      "name": "Example Customer",
      "total_spending": 12345
    }
  ]
}
```

### Clarification response

For an ambiguous question such as `Who is the best customer?`, the API may ask the user to select a metric before continuing.

```json
{
  "question": "Who is the best customer?",
  "selected_option": "total_spending"
}
```

Send the selected option with the original question to continue:

```json
{
  "question": "Who is the best customer?",
  "selected_option": "total_spending"
}
```

The API response uses `status: "clarification_required"` when clarification is needed and `status: "completed"` when analysis finishes. The clarification options returned by the API contain `value` and `label` fields; use a returned `value` as `selected_option`.

## Running tests

Run the Python tests from the repository root with the virtual environment activated:

```powershell
python -m pytest -q
```

You can run a focused validator test separately:

```powershell
python -m pytest backend/app/services/test_sql_validator.py -q
```

**Testing note:** Some current service and API tests invoke the live Groq model. They can fail if the API key is invalid, the service is unavailable, or the account hits a rate limit. Mocking LLM calls for routine unit tests and keeping live-model checks separate is a planned testing improvement. A successful focused test run does not imply that the full suite has passed.

## Security and limitations

- Keep `.env`, API keys, and database credentials out of source control. If a real secret was exposed, rotate it.
- Generated SQL must be validated before execution. Validation is a defense-in-depth measure, not a substitute for least-privilege database credentials, timeouts, query limits, and careful review.
- Use a PostgreSQL role with only the permissions the application requires; do not connect as a superuser in production.
- The current frontend stores recent analysis history in browser `localStorage`; it is not a server-side user account or shared history store.
- The LLM depends on the external Groq service, so rate limits and service availability can affect analysis.
- The project is under active development and has not been documented here as production-hardened.

## Roadmap

Potential next steps include:

- Mock LLM responses in unit tests and isolate live integration tests.
- Expand SQL-validation coverage and harden query execution limits and timeouts.
- Improve structured logging and error handling.
- Add broader analysis scenarios and regression tests for filters, aggregations, joins, and dates.
- Improve deployment configuration and CORS management.
- Add screenshots or a short demo GIF to showcase the interface.

## License

No license file was present in the reviewed project archive. Add a `LICENSE` file before presenting the repository as open source under a specific license.
