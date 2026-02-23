# Prospecting Icebreaker Generator

A Streamlit web app that generates bespoke sales prospecting icebreaker emails. The app acts as a UI and API client for two CrewAI Enterprise crews that handle all AI-powered research and content generation.

## How It Works

The app has three steps:

1. **Company Research** -- The user provides their own company name, domain, and optional context. The app kicks off **Crew 1** to research the company's products, services, and value propositions. The result is a detailed company reconnaissance report.

2. **Prospect & Generate** -- The user provides information about the entity they want to prospect to (company name, individual name, and/or talking points). The app kicks off **Crew 2** with the company recon report plus the prospect details, which researches the prospect and generates a tailored icebreaker email.

3. **Review & Iterate** -- The generated email is displayed for the user to copy. They can go back and prospect to a different entity (keeping the company research) or start over entirely.

---

## CrewAI Enterprise Crews

This app depends on two crews deployed on CrewAI Enterprise (AOP). Each crew is called via the standard REST API (`POST /kickoff`, `GET /status/{id}`).

### Crew 1: Company Reconnaissance

**Purpose:** Research the seller's own company to understand their products, services, competitive advantages, and value propositions. This report serves as context for all subsequent prospecting emails.

**Inputs:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | Yes | Name of the seller's company |
| `company_domain` | string | Yes | Company website domain (e.g. `example.com`) |
| `supplemental_info` | string | No | Additional context -- specific products to highlight, target market, recent news, etc. |

**Expected Output:** A comprehensive text report covering:
- What the company does (products/services)
- Key value propositions and differentiators
- Target market and ideal customer profile
- Recent news, achievements, or notable content
- Any information from the supplemental context

### Crew 2: Prospecting Icebreaker

**Purpose:** Research the prospect (company and/or individual) and generate a personalized icebreaker email that connects the seller's offerings to the prospect's needs.

**Inputs:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | Yes | Seller's company name (from Step 1) |
| `company_domain` | string | Yes | Seller's domain (from Step 1) |
| `supplemental_info` | string | No | Seller's supplemental context (from Step 1) |
| `recon_report` | string | Yes | Full company recon report (output of Crew 1) |
| `prospect_company` | string | No | Name of the company being prospected to |
| `prospect_name` | string | No | Name of the individual being prospected to |
| `supplemental_prospect_info` | string | No | Specifics about what to sell, known info about the prospect, desired talking points, etc. |

**Expected Output:** A ready-to-send icebreaker email as plain text, including:
- Personalized subject line
- Opening that references something specific about the prospect
- Connection between the prospect's needs and the seller's offerings
- Clear call to action
- Professional sign-off

---

## Local Development

### Prerequisites

- Python 3.12+
- CrewAI Enterprise crews deployed with valid URLs and tokens

### Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd crewai-prospecting-icebreaker

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your actual crew URLs and tokens

# Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## Heroku Deployment

### First-time setup

```bash
# Create the Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set CREW1_URL=https://your-company-recon-crew.crewai.com
heroku config:set CREW1_TOKEN=your-crew1-bearer-token
heroku config:set CREW2_URL=https://your-prospecting-crew.crewai.com
heroku config:set CREW2_TOKEN=your-crew2-bearer-token

# Deploy (if using Heroku git remote)
git push heroku main
```

Or connect your GitHub repo via the Heroku Dashboard (Deploy tab > GitHub) for automatic deploys on push.

### How it runs

Heroku reads the `Procfile` and starts Streamlit with the dynamically assigned `$PORT`. The `.python-version` file tells Heroku to use Python 3.12. No buildpack configuration is needed -- Heroku auto-detects Python from `requirements.txt`.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CREW1_URL` | Base URL for the Company Reconnaissance crew |
| `CREW1_TOKEN` | Bearer token for Crew 1 authentication |
| `CREW2_URL` | Base URL for the Prospecting Icebreaker crew |
| `CREW2_TOKEN` | Bearer token for Crew 2 authentication |

---

## Project Structure

```
app.py                  # Streamlit UI -- three-phase workflow
api_client.py           # CrewAI Enterprise API client (kickoff + poll)
requirements.txt        # Python dependencies
Procfile                # Heroku process declaration
.python-version         # Python version for Heroku
.streamlit/config.toml  # Streamlit config for local dev
.env.example            # Environment variable template
```
