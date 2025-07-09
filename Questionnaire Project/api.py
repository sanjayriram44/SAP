import os
import asyncio
from typing import List, Dict
from user_choices import current_user_choices
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn

from './BBP Generation/generate_bbp.py' import generate_bbp_from_qa

from dotenv import load_dotenv
from process_analysis import (
    generate_process_understanding,
    update_process_understanding_with_input,
    generate_process_recommendation
)

load_dotenv(dotenv_path="local.env", override=True)


conversation_history = []

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

class ConversationHistoryRequest(BaseModel):
    history: List[Dict]

class QAInput(BaseModel):
    question: str
    answer: str

class CorrectionUpdateRequest(BaseModel):
    history: List[Dict]
    correction: str
    current_understanding: str

class CustomerContextRequest(BaseModel):
    context: Dict[str, str]
    
def add_main_qa(question: str, answer: str):
    conversation_history.append({
        "question": question,
        "answer": answer,
        "followups": []
    })
def add_followup(followup_question: str, followup_answer: str):
    if not conversation_history:
        raise ValueError("No main Q&A exists yet.")
    conversation_history[-1]["followups"].append({
        "question": followup_question,
        "answer": followup_answer
    })





@app.post("/update_sap_product")
async def update_sap_product(product: str = Body(...)):
    try:
        current_user_choices["product"] = product
        print(f"[PRODUCT UPDATED] {product}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.post("/update_module")
async def update_module(module: str = Body(...)):
    try:
        current_user_choices["module"] = module
        print(f"[MODULE UPDATED] {module}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.post("/update_activity")
async def update_activity(activity: str = Body(...)):
    try:
        current_user_choices["activity"] = activity
        print(f"[ACTIVITY UPDATED] {activity}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.post("/update_customer_context")
async def update_customer_context(payload: Dict[str, Dict[str, str]]):
    try:
        context = payload.get("context", {})
        for key, value in context.items():
            current_user_choices[key] = value
        print("[CONTEXT UPDATED]", context)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
    
app.post("/update_bbp_generation_journey")
async def update_sap_product(product: str = Body(...)):
    try:
        current_user_choices["product"] = product
        print(f"[PRODUCT UPDATED] {product}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")



@app.post("/generate_process_understanding")
async def get_process_understanding(request: ConversationHistoryRequest):
    try:
        result = await run_in_threadpool(generate_process_understanding, request.history)
        return {"process_understanding": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_process_understanding")
async def update_process_understanding(request: CorrectionUpdateRequest):
    try:
        result = await run_in_threadpool(
            update_process_understanding_with_input,
            request.history,
            request.correction,
            request.current_understanding
        )
        return {"updated_process_understanding": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_process_recommendation")
async def get_process_recommendation(request: ConversationHistoryRequest):
    try:
        result = await run_in_threadpool(generate_process_recommendation, request.history)
        return {"process_recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
