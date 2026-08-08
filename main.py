from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import os
import time

app = FastAPI(title="SportyBet Coupon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPORTYBET_BASE = "https://sportybet.com"

class BetPlaceRequest(BaseModel):
    selections: List[Dict[str, Any]]
    stake: float
    currency: str = "NGN"

class SportyBetClient:
    def __init__(self):
        self.base = SPORTYBET_BASE
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://sportybet.com",
            "Referer": "https://sportybet.com/",
        }
    
    async def _request(self, method: str, path: str, data: dict = None) -> dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0, follow_redirects=True) as client:
            try:
                url = f"{self.base}{path}"
                resp = await client.request(method, url, json=data)
                try:
                    return resp.json()
                except:
                    return {"error": "Invalid JSON response"}
            except Exception as e:
                return {"error": str(e)}
    
    async def get_bet_slip(self, booking_code: str) -> dict:
        return await self._request("GET", f"/betpro/bet-slip/{booking_code}?provider=sportybet")
    
    async def place_bet(self, selections: list, stake: float, currency: str = "NGN") -> dict:
        data = {
            "selections": selections,
            "stake": stake,
            "currency": currency,
            "timestamp": int(time.time() * 1000)
        }
        return await self._request("POST", "/api/v1/bet/book", data)

@app.get("/")
async def root():
    return {"service": "SportyBet Coupon API", "status": "online"}

@app.get("/bet/slip/{booking_code}")
async def get_bet_slip(booking_code: str):
    if not booking_code or len(booking_code) != 8:
        raise HTTPException(status_code=400, detail="Booking code must be 8 characters")
    
    client = SportyBetClient()
    result = await client.get_bet_slip(booking_code.upper())
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return {"success": True, "data": result, "booking_code": booking_code}

@app.post("/bet/place")
async def place_bet(request: BetPlaceRequest):
    if not request.selections or len(request.selections) == 0:
        raise HTTPException(status_code=400, detail="Selections required")
    
    if request.stake <= 0:
        raise HTTPException(status_code=400, detail="Valid stake required")
    
    client = SportyBetClient()
    result = await client.place_bet(request.selections, request.stake, request.currency)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return {
        "success": True,
        "data": result,
        "booking_code": result.get("booking_code"),
        "message": "Bet placed successfully"
    }

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SportyBet Coupon API</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: system-ui, sans-serif; background: #0a0a0f; color: #e4e4e7; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { max-width: 560px; width: 100%; background: #18181b; border: 1px solid #27272a; border-radius: 16px; padding: 28px; }
        h1 { font-size: 1.6rem; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #71717a; font-size: 0.85rem; margin-bottom: 1.5rem; }
        .tab-bar { display: flex; gap: 4px; margin-bottom: 1.5rem; background: #0a0a0f; border-radius: 8px; padding: 4px; }
        .tab { flex: 1; padding: 8px; text-align: center; border: none; background: transparent; color: #71717a; font-size: 0.75rem; font-weight: 500; border-radius: 6px; cursor: pointer; }
        .tab.active { background: #18181b; color: #e4e4e7; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; font-size: 0.7rem; text-transform: uppercase; color: #a1a1aa; margin-bottom: 4px; }
        input, textarea { width: 100%; padding: 10px 12px; background: #0a0a0f; border: 1px solid #27272a; border-radius: 8px; color: #e4e4e7; font-size: 0.85rem; outline: none; }
        input:focus, textarea:focus { border-color: #3b82f6; }
        textarea { resize: vertical; font-family: monospace; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; margin-top: 8px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; }
        .btn:hover { transform: translateY(-1px); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .result { margin-top: 1rem; padding: 12px; border-radius: 8px; font-size: 0.8rem; font-family: monospace; white-space: pre-wrap; word-break: break-word; max-height: 300px; overflow-y: auto; background: #0a0a0f; border: 1px solid #27272a; display: none; }
        .result.success { display: block; border-color: #166534; color: #86efac; }
        .result.error { display: block; border-color: #7f1d1d; color: #fca5a5; }
        .result.loading { display: block; border-color: #2a2a4a; color: #93c5fd; }
        .footer { margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #1a1a1a; font-size: 0.6rem; color: #3f3f46; text-align: center; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 9999px; background: #3b82f6; color: white; font-size: 0.55rem; font-weight: 600; }
        .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
        .status-dot.online { background: #4ade80; }
        .status { font-size: 0.7rem; color: #71717a; }
    </style>
</head>
<body>
<div class="container">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <h1>⚽ SportyBet</h1>
        <span class="badge">Coupon API</span>
    </div>
    <p class="subtitle">Coupon = Booking Code (e.g., 009BE4F2)</p>
    
    <div class="tab-bar">
        <button class="tab active" data-tab="slip">Bet Slip</button>
        <button class="tab" data-tab="bet">Place Bet</button>
    </div>
    
    <div id="slip" class="tab-content active">
        <div class="form-group">
            <label>Booking Code</label>
            <input id="bookingCode" placeholder="e.g. 009BE4F2" maxlength="8" />
        </div>
        <button class="btn" id="slipBtn">Get Bet Slip</button>
        <div id="slipResult" class="result"></div>
    </div>
    
    <div id="bet" class="tab-content">
        <div class="form-group">
            <label>Selections (JSON)</label>
            <textarea id="selections" rows="4" placeholder='[{"eventId":"sr:match:123","marketId":"1","outcomeId":"1"}]'></textarea>
        </div>
        <div class="form-group">
            <label>Stake (NGN)</label>
            <input id="stake" type="number" placeholder="100" />
        </div>
        <button class="btn" id="betBtn">Place Bet</button>
        <div id="betResult" class="result"></div>
    </div>
    
    <div class="footer">
        <span class="status"><span class="status-dot online"></span> Backend proxies SportyBet API calls</span>
    </div>
</div>

<script>
    const tabs = document.querySelectorAll('.tab');
    const contents = { slip: document.getElementById('slip'), bet: document.getElementById('bet') };
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            Object.keys(contents).forEach(key => {
                contents[key].classList.toggle('active', key === tab.dataset.tab);
            });
        });
    });
    
    function showResult(element, message, type = 'loading') {
        element.className = 'result ' + type;
        element.textContent = message;
    }
    
    async function apiCall(endpoint, method = 'GET', data = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (data) options.body = JSON.stringify(data);
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return response.json();
    }
    
    document.getElementById('slipBtn').addEventListener('click', async () => {
        const code = document.getElementById('bookingCode').value;
        const resultEl = document.getElementById('slipResult');
        
        if (!code || code.length !== 8) {
            showResult(resultEl, 'Booking code must be 8 characters', 'error');
            return;
        }
        
        showResult(resultEl, 'Fetching...', 'loading');
        try {
            const data = await apiCall(`/bet/slip/${code.toUpperCase()}`);
            showResult(resultEl, JSON.stringify(data.data, null, 2), 'success');
        } catch (e) {
            showResult(resultEl, `Error: ${e.message}`, 'error');
        }
    });
    
    document.getElementById('betBtn').addEventListener('click', async () => {
        const selections = document.getElementById('selections').value;
        const stake = document.getElementById('stake').value;
        const resultEl = document.getElementById('betResult');
        
        if (!selections) {
            showResult(resultEl, 'Please enter selections', 'error');
            return;
        }
        if (!stake || parseFloat(stake) <= 0) {
            showResult(resultEl, 'Valid stake required', 'error');
            return;
        }
        
        let parsedSelections;
        try { parsedSelections = JSON.parse(selections); } catch {
            showResult(resultEl, 'Invalid JSON format', 'error');
            return;
        }
        
        showResult(resultEl, 'Placing bet...', 'loading');
        try {
            const data = await apiCall('/bet/place', 'POST', {
                selections: parsedSelections,
                stake: parseFloat(stake)
            });
            showResult(resultEl, JSON.stringify(data.data, null, 2), 'success');
        } catch (e) {
            showResult(resultEl, `Error: ${e.message}`, 'error');
        }
    });
</script>
</body>
</html>
"""

@app.get("/ui")
async def serve_ui():
    return HTMLResponse(HTML)
