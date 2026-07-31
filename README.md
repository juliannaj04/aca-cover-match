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

## Structure

- `zip_lookup.py` — ZIP → county → CMS rating area
- `subsidy.py` — ACA premium tax credit math
- `match_engine.py` — combines lookup + subsidy + plan data into one match
- `explain.py` — Claude-generated plain-English explanation of top plans
- `app.py` — Flask API (`/match`, `/health`)
- `frontend/` — React form + results UI

<img width="1122" height="919" alt="Screenshot 2026-07-31 at 11 31 22 AM" src="https://github.com/user-attachments/assets/8d8360d0-f748-42c0-8ab7-d85457c5a73d" />
<img width="1129" height="905" alt="Screenshot 2026-07-31 at 11 31 05 AM" src="https://github.com/user-attachments/assets/63db1788-63cc-4323-99a0-81ef660dfc53" />
<img width="1117" height="602" alt="Screenshot 2026-07-31 at 11 30 50 AM" src="https://github.com/user-attachments/assets/875c948f-4963-439a-b064-4b5b63cf9534" />
