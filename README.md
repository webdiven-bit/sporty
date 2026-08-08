# SportyBet Coupon API

FastAPI backend for SportyBet betting coupon operations.

## Features

- Get bet slip from booking code (the "coupon")
- Place bets and get booking codes
- Web UI at `/ui`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/bet/slip/{code}` | Get bet slip from booking code |
| POST | `/bet/place` | Place bet and get booking code |

## Deploy on Render

1. Push this repo to GitHub
2. Create a Web Service on Render
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
