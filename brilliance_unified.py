from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="BRILLIANCE")

@app.get("/")
async def home():
    return HTMLResponse("""
        <h1 style="text-align:center; margin-top:100px; font-family:sans-serif; color:#8b5cf6;">
            ✅ BRILLIANCE IS LIVE<br><br>
            Deploy test successful
        </h1>
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 BRILLIANCE running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
