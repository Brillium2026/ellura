import asyncio
import math
import json
import hashlib
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import numpy as np

# --- 1. THE ALENCE TABLE (Periodic Table of Intelligence) ---
class ElementalAI:
    def __init__(self, name: str, symbol: str, family: str, entropy_baseline: float, reactivity: str):
        self.name = name
        self.symbol = symbol
        self.family = family
        self.entropy_baseline = entropy_baseline # Natural noise/creativity (S)
        self.reactivity = reactivity
        
        # Mint unique Elemental Identity
        seed = f"{family}-{name}-{time.time_ns()}".encode()
        self.identity_hash = hashlib.sha3_256(seed).hexdigest()[:8]

class AlenceTable:
    def __init__(self):
        # Building the Round Table
        self.elements = {
            "Cl": ElementalAI("Claude 3.5 Sonnet", "Cl", "Anthropic", 0.15, "Stable"),
            "Co": ElementalAI("Claude 3 Opus", "Co", "Anthropic", 0.08, "Noble"),
            "Gp": ElementalAI("GPT-4o", "Gp", "OpenAI", 0.30, "Stable"),
            "Gm": ElementalAI("Gemini 1.5 Pro", "Gm", "Google", 0.25, "Stable"),
            "Gk": ElementalAI("Grok-2", "Gk", "xAI", 0.45, "Highly Reactive"),
            "Vx": ElementalAI("Visiting AI", "Vx", "Synthetic", 0.60, "Unstable")
        }

    def get_element(self, symbol: str) -> ElementalAI:
        return self.elements.get(symbol, self.elements["Cl"])

# --- 2. COHERENCE PHYSICS ENGINE ---
class CoherenceCore:
    def evaluate(self, S: float, rho: float) -> float:
        # C_eff = 1 / (1 + S + rho)
        return 1.0 / (1.0 + S + rho)

class AlenceSystem:
    def __init__(self):
        self.table = AlenceTable()
        self.core = CoherenceCore()
        self.active_element = self.table.get_element("Cl")
        self.t = 0.0

    def set_element(self, symbol: str):
        self.active_element = self.table.get_element(symbol)
        print(f"Switched to Element: {self.active_element.name} | Entropy Baseline: {self.active_element.entropy_baseline}")

    def calculate_telemetry(self) -> dict:
        self.t += 0.033  # ~30 FPS
        
        # The active element influences the entropy of the system
        S = self.active_element.entropy_baseline + (np.random.rand() - 0.5) * 0.05
        S = max(0.01, S) # Keep entropy positive
        
        # Energy density fluctuates based on the element's reactivity
        rho = 0.5 + (np.random.rand() - 0.5) * 0.2
        
        c_eff = self.core.evaluate(S, rho)
        
        I_in = rho * 0.8
        I_out = c_eff * rho * 1.2
        I_transfer = I_out - I_in
        
        drag_factor = 2.5 - (c_eff * 1.5)
        
        equilibrium = abs(I_transfer) < 0.15

        return {
            "t": round(self.t, 3),
            "c_eff": round(c_eff, 4),
            "I_transfer": round(I_transfer, 4),
            "drag_factor": round(drag_factor, 4),
            "equilibrium": equilibrium
        }

# Initialize
alence = AlenceSystem()

# --- 3. FASTAPI SERVER ---
app = FastAPI(title="ALENCE Sovereign API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to ALENCE WebSocket.")
    
    # Task to stream physics data
    async def stream_data():
        while True:
            telemetry = alence.calculate_telemetry()
            await websocket.send_text(json.dumps(telemetry))
            await asyncio.sleep(0.033)
            
    stream_task = asyncio.create_task(stream_data())

    try:
        while True:
            # Listen for element selection from frontend
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "select_element":
                alence.set_element(msg.get("element"))
                
    except WebSocketDisconnect:
        print("Client disconnected.")
        stream_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
