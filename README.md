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

<img width="1117" height="602" alt="Screenshot 2026-07-31 at 11 30 50 AM" src="https://github.com/user-attachments/assets/cd9621ee-3680-46e3-89bb-d0a0246b67a2" />

<img width="1129" height="905" alt="Screenshot 2026-07-31 at 11 31 05 AM" src="https://github.com/user-attachments/assets/859a7908-44d2-4cd2-a22d-89dc3f29c222" />

<img width="1122" height="919" alt="Screenshot 2026-07-31 at 11 31 22 AM" src="https://github.com/user-attachments/assets/198550d3-9424-4ce3-8bda-fc941896fa2f" />



