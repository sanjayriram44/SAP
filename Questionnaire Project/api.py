import os
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn

from dotenv import load_dotenv
from process_analysis import (
    generate_process_understanding,
    update_process_understanding_with_input,
    generate_process_recommendation
)

# ------------------- Environment Setup -------------------

load_dotenv(dotenv_path="local.env", override=True)

# ------------------- FastAPI App Initialization -------------------

app = FastAPI(
    title="SAP BBP Discovery Assistant API",
    description="API backend for SAP Ariba BBP process understanding and recommendation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Schema Definitions -------------------

class ConversationHistoryRequest(BaseModel):
    history: List[Dict]

class CorrectionUpdateRequest(BaseModel):
    history: List[Dict]
    correction: str
    current_understanding: str

# ------------------- API Endpoints -------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate_process_understanding")
async def get_process_understanding(request: ConversationHistoryRequest):
    """
    Generate process understanding summary based on discovery conversation history.
    """
    try:
        result = await run_in_threadpool(generate_process_understanding, request.history)
        return {"process_understanding": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/update_process_understanding")
async def update_process_understanding(request: CorrectionUpdateRequest):
    """
    Update process understanding based on user's correction input.
    """
    try:
        result = await run_in_threadpool(
            update_process_understanding_with_input,
            request.history,
            request.correction,
            request.current_understanding
        )
        return {"updated_process_understanding": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/generate_process_recommendation")
async def get_process_recommendation(request: ConversationHistoryRequest):
    """
    Generate SAP Ariba To-Be process recommendation from discovery Q&A.
    """
    try:
        result = await run_in_threadpool(generate_process_recommendation, request.history)
        return {"process_recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ------------------- Main Entry -------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
