# ACA Plan Matcher

Matches NC ACA marketplace plans to a household's income/ZIP/age, applies the premium tax credit, and generates a plain-English explanation of the top options via Claude.

## Setup

```bash
# backend
pip install flask flask-cors pandas anthropic python-dotenv
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# frontend
cd frontend
npm install
```

## Run

```bash
# terminal 1 (from project root)
python3 app.py

# terminal 2
npm run dev --prefix frontend
```

Open the printed `localhost:5173` URL.

## Structure

- `zip_lookup.py` — ZIP → county → CMS rating area
- `subsidy.py` — ACA premium tax credit math
- `match_engine.py` — combines lookup + subsidy + plan data into one match
- `explain.py` — Claude-generated plain-English explanation of top plans
- `app.py` — Flask API (`/match`, `/health`)
- `frontend/` — React form + results UI
