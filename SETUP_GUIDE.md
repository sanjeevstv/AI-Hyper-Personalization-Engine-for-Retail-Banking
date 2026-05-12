# Setup Guide — AI/GenAI Hyper-Personalization Engine for Retail Banking

Complete setup instructions for macOS and Windows.

---

## Prerequisites

| Requirement | Version | Check command |
|-------------|---------|---------------|
| **Python** | 3.10 or higher | `python3 --version` (macOS) / `python --version` (Windows) |
| **Node.js** | 18 or higher | `node --version` |
| **npm** | 9 or higher | `npm --version` |
| **Git** | Any recent | `git --version` |

### Installing Prerequisites

**macOS** (using Homebrew):
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Node.js
brew install python@3.12 node
```

**Windows**:
1. Download and install Python from https://www.python.org/downloads/ — check "Add Python to PATH" during installation
2. Download and install Node.js LTS from https://nodejs.org/
3. Restart your terminal after installation

---

## Project Structure

```
Capstone_proj/
├── backend/                  # Flask REST API
│   ├── app.py                # Application entry point
│   ├── config.py             # Configuration (DB, OpenAI)
│   ├── extensions.py         # SQLAlchemy instance
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variable template
│   ├── generate_seed_data.py # Synthetic data generator
│   ├── test_integration.py   # Integration test suite
│   ├── models/
│   │   └── models.py         # Database models (7 tables)
│   ├── services/
│   │   ├── ingestion.py      # Data loading & validation
│   │   ├── profiler.py       # Customer profile computation
│   │   ├── life_events.py    # Life event detection (rule + AI)
│   │   ├── segmentation.py   # K-Means clustering
│   │   ├── recommendation.py # Product recommendations (rule + AI)
│   │   └── genai_messaging.py# OpenAI message generation
│   ├── routes/
│   │   ├── customers.py      # Customer & segment endpoints
│   │   ├── ingestion.py      # Data upload endpoints
│   │   ├── recommendations.py# Recommendation endpoints
│   │   └── messaging.py      # GenAI messaging endpoints
│   └── seed_data/            # Sample CSV datasets
│       ├── customers.csv
│       ├── transactions.csv
│       ├── digital_behavior.csv
│       └── products.csv
├── frontend/                 # React dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/client.js     # API client functions
│       └── components/       # React components
└── README.md
```

---

## Step 1 — Clone or Copy the Project

```bash
# If using Git
git clone <repository-url>
cd Capstone_proj

# Or simply copy the entire Capstone_proj folder to your machine
```

---

## Step 2 — Backend Setup

### macOS

```bash
# Navigate to backend
cd backend

# (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
```

### Windows (Command Prompt)

```cmd
:: Navigate to backend
cd backend

:: (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate

:: Install Python dependencies
pip install -r requirements.txt

:: Create your environment file
copy .env.example .env
```

### Windows (PowerShell)

```powershell
# Navigate to backend
cd backend

# (Recommended) Create a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Create your environment file
Copy-Item .env.example .env
```

### Note on psycopg2-binary

If `pip install` fails on the `psycopg2-binary` package (common on Windows without PostgreSQL installed), you can safely remove it from `requirements.txt` since the project uses SQLite by default. Just delete the line `psycopg2-binary` from the file and re-run `pip install -r requirements.txt`.

---

## Step 3 — Configure Environment Variables

Open the `.env` file in `backend/` and update the values:

```env
# Database — SQLite is the default (no setup needed)
# To use PostgreSQL instead, uncomment and set:
# DATABASE_URL=postgresql://user:password@localhost:5432/banking_personalization

# OpenAI / LLM Configuration (required for AI-powered features)
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# Flask environment
FLASK_ENV=development
```

**If using standard OpenAI:**
- Set `OPENAI_API_KEY` to your OpenAI API key
- Set `OPENAI_BASE_URL` to `https://api.openai.com/v1`
- Set `OPENAI_MODEL` to `gpt-3.5-turbo` or `gpt-4`

**If using a custom OpenAI-compatible endpoint:**
- Set `OPENAI_BASE_URL` to your endpoint URL
- Set `OPENAI_MODEL` to the model name your platform supports

**If you don't have an API key:**
- Leave `OPENAI_API_KEY` empty — the app will still work fully using rule-based logic with template fallback for messaging. You can toggle between Rule-Based and AI-Powered in the dashboard; AI mode will gracefully fall back to rules if no key is configured.

---

## Step 4 — Start the Backend Server

### macOS

```bash
cd backend
source venv/bin/activate    # if using virtual environment
python3 app.py
```

### Windows

```cmd
cd backend
venv\Scripts\activate       :: if using virtual environment
python app.py
```

You should see:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

Keep this terminal open. The API is now running at **http://localhost:5001**.

---

## Step 5 — Frontend Setup

Open a **new terminal window** (keep the backend running in the first one).

### macOS and Windows (same commands)

```bash
# Navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

You should see:

```
VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:3000/
```

The frontend is now running at **http://localhost:3000**.

---

## Step 6 — Initialize and Use the Application

1. Open **http://localhost:3000** in your web browser

2. You will see the **System Initialization** screen. Click **"Initialize System"**. This runs 4 steps automatically:
   - Loads seed data (100 customers, ~4,000 transactions, 10 products)
   - Computes customer financial profiles
   - Detects life events from transaction patterns
   - Runs K-Means segmentation into 5 clusters

3. Click **"Open Dashboard"** when initialization completes

4. **Customer View tab:**
   - Use the filters (Customer ID, Segment, City, Occupation, Date Range, Age Range) and click **Go**
   - Click any customer row to expand and see their full profile, life events, recommendations, and messaging
   - Toggle between **Rule-Based** and **AI-Powered** for life events and recommendations

5. **Segment Overview tab:**
   - View K-Means segment distribution with charts
   - Click any segment card to drill down into customer lists
   - Use sub-filters (City, Occupation, Age) to narrow results
   - Export filtered data to CSV

---

## Running Tests

### macOS

```bash
cd backend
source venv/bin/activate
python3 test_integration.py
```

### Windows

```cmd
cd backend
venv\Scripts\activate
python test_integration.py
```

Expected output: **57 passed, 0 failed**.

---

## Troubleshooting

### Port 5001 already in use

**macOS:** Port 5000/5001 may be used by AirPlay Receiver. Go to **System Settings > General > AirDrop & Handoff** and disable AirPlay Receiver, or change the port in `backend/app.py` (line 32) and `frontend/vite.config.js` (line 10) to another port like 5002.

**Windows:** Find and kill the process using the port:
```cmd
netstat -ano | findstr :5001
taskkill /PID <PID_NUMBER> /F
```

### Port 3000 already in use

Change the port in `frontend/vite.config.js` (line 7) to another port like 3001.

### "Module not found" errors in Python

Make sure your virtual environment is activated:
- macOS: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

Then re-run `pip install -r requirements.txt`.

### psycopg2-binary install fails on Windows

Remove the `psycopg2-binary` line from `backend/requirements.txt`. It's only needed for PostgreSQL; the default SQLite works without it.

### AI features show "fallback" or "connection error"

- Verify your `.env` file has a valid `OPENAI_API_KEY`
- Check that `OPENAI_BASE_URL` is correct for your provider
- Ensure your machine has internet access to reach the API endpoint
- The app still works fully in rule-based mode without an API key

### Frontend shows "Request failed with status code 500" on Initialize

- Make sure the backend is running in a separate terminal
- Check that the backend is on port 5001 (look at the terminal output)
- Verify the Vite proxy target in `frontend/vite.config.js` matches the backend port

### npm install fails

- Ensure Node.js 18+ is installed: `node --version`
- Try clearing the cache: `npm cache clean --force` then `npm install`

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | SQLite file in `backend/` | Database connection string. Default uses SQLite (zero setup). Set to a PostgreSQL URL to use Postgres. |
| `OPENAI_API_KEY` | No | (empty) | API key for OpenAI-compatible LLM. When empty, AI features fall back to rule-based logic. |
| `OPENAI_BASE_URL` | No | (empty) | Custom base URL for OpenAI-compatible APIs. Leave empty for standard OpenAI (`https://api.openai.com/v1`). |
| `OPENAI_MODEL` | No | `gpt-3.5-turbo` | Model name to use for AI features. |
| `FLASK_ENV` | No | `production` | Set to `development` for debug mode. |

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ingest/seed` | Load built-in seed data |
| POST | `/api/ingest/upload` | Upload custom CSV dataset |
| GET | `/api/customers/?q=` | Search customers |
| GET | `/api/customers/<id>` | Full customer view (profile + segment + events) |
| GET | `/api/customers/filter?segment=&city=&occupation=&age_min=&age_max=` | Filter customers |
| GET | `/api/customers/filter-options` | Get distinct values for filter dropdowns |
| GET | `/api/customers/export?...` | Export filtered customers as CSV |
| POST | `/api/customers/compute-profiles` | Compute all customer profiles |
| POST | `/api/customers/detect-life-events` | Run life event detection |
| POST | `/api/customers/run-segmentation` | Run K-Means segmentation |
| GET | `/api/customers/<id>/profile` | Customer financial profile |
| GET | `/api/customers/<id>/life-events?mode=rule\|ai` | Life events (toggle rule/AI) |
| GET | `/api/customers/<id>/segment` | Customer segment assignment |
| GET | `/api/customers/<id>/recommendations?mode=rule\|ai` | Product recommendations (toggle rule/AI) |
| POST | `/api/customers/<id>/generate-message` | Generate personalized message |
| GET | `/api/customers/segments/overview` | K-Means segment distribution |
| GET | `/api/customers/segments/by-city` | Customer count by city |
| GET | `/api/customers/segments/by-occupation` | Customer count by occupation |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Axios |
| Backend | Python, Flask, SQLAlchemy, Flask-CORS |
| Database | SQLite (default) / PostgreSQL (optional) |
| AI/ML | Scikit-learn (K-Means), Pandas, NumPy |
| GenAI | OpenAI-compatible API (GPT, Claude, or any compatible endpoint) |
| Data Generation | Faker |
