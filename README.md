# AI/GenAI Hyper-Personalization Engine for Retail Banking

A full-stack AI-powered personalization engine that analyzes customer transaction behavior and life events to recommend banking products and generate personalized engagement messages.

> For detailed setup instructions (macOS and Windows), see **[SETUP_GUIDE.md](SETUP_GUIDE.md)**.

## Demo

https://github.com/sanjeevstv/AI-Hyper-Personalization-Engine-for-Retail-Banking/releases/download/v1.0.0/demo.mp4

## Architecture

- **Backend**: Python Flask REST API with SQLAlchemy ORM
- **Frontend**: React 18 + Vite + Tailwind CSS dashboard
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **AI/ML**: Scikit-learn K-Means clustering for customer segmentation
- **GenAI**: OpenAI-compatible API for personalized messaging and AI-powered recommendations (with rule-based fallback)

## Features

1. **Data Ingestion** — Load CSV/JSON banking datasets with validation
2. **Customer Profile Builder** — Compute financial profiles from transaction data
3. **Life Event Detection** — Rule-based + AI-powered engine detecting promotions, travel patterns, new parents, home buyers, etc.
4. **Customer Segmentation** — K-Means clustering into 5 segments (Premium, Travelers, Savers, Investors, Credit Seekers)
5. **Recommendation Engine** — Top-3 personalized product recommendations with toggle between rule-based scoring and AI reasoning
6. **GenAI Messaging** — Personalized emails, push notifications, RM talking points, chatbot responses
7. **Dashboard** — React UI with advanced filtering (segment, city, occupation, age, date range), expandable customer views, segment drill-down with CSV export

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) OpenAI-compatible API key for AI-powered features

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # macOS
# python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your API key
python3 app.py         # python app.py on Windows
```

The API runs at **http://localhost:5001**.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

### First Run

1. Click **"Initialize System"** — loads seed data, computes profiles, detects life events, runs segmentation
2. Go to **Customer View** — filter by segment, city, occupation, age, or date range, then click **Go**
3. Click any customer row to expand and see profile, life events, recommendations, and messaging
4. Toggle between **Rule-Based** and **AI-Powered** for life events and recommendations
5. Go to **Segment Overview** — view K-Means distribution, click segments to drill down, export to CSV

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | SQLite file | Database connection string |
| `OPENAI_API_KEY` | (empty) | API key for AI features. Leave empty for rule-based only. |
| `OPENAI_BASE_URL` | (empty) | Custom endpoint URL for OpenAI-compatible APIs |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | Model name for AI features |

## Running Tests

```bash
cd backend
python3 test_integration.py   # python test_integration.py on Windows
```

Runs 57 end-to-end tests covering all modules.

## Full Documentation

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for:
- Detailed macOS and Windows setup instructions
- Virtual environment setup
- Troubleshooting common issues
- Complete API endpoint reference
- Tech stack details
