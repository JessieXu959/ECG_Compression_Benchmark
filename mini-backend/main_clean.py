#!/usr/bin/env python3
"""
ECG Compression Challenge - Mini Backend
FastAPI application for handling submissions and leaderboard
"""

import os
import uuid
import shutil
import json
import time
import zipfile
import asyncio
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuration
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp")
SCORING_DIR = Path("scoring")
DATA_DIR = Path("data")

# Create directories if they don't exist
for directory in [UPLOAD_DIR, TEMP_DIR, SCORING_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="ECG Compression Challenge Backend",
    description="Mini backend for ECG compression algorithm evaluation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserRegister(BaseModel):
    teamName: str
    email: str
    password: str

class UserLogin(BaseModel):
    teamName: str
    password: str

class SubmissionResponse(BaseModel):
    submission_id: str
    status: str
    message: str

# In-memory storage for demo (in production, use a proper database)
users_db = {}
submissions_db = {}

# Data cleanup function (add this after the database definitions)
def clear_demo_data():
    """Clear demo data keeping only real user accounts"""
    real_teams = ["teamA"]

    # Clear demo submissions
    to_remove = []
    for sub_id, sub in submissions_db.items():
        if sub.get("teamName") not in real_teams:
            to_remove.append(sub_id)

    for sub_id in to_remove:
        del submissions_db[sub_id]

    # Clear demo users
    to_remove = []
    for team_name in users_db.keys():
        if team_name not in real_teams:
            to_remove.append(team_name)

    for team_name in to_remove:
        del users_db[team_name]

    print(f"🧹 Cleared demo data. Keeping {len(real_teams)} real teams.")
    return len(to_remove)

# Add cleanup endpoint
@app.post("/api/admin/clear-demo-data")
async def clear_demo_data_endpoint():
    """Admin endpoint to clear demo data"""
    removed_count = clear_demo_data()
    return {
        "status": "success",
        "message": f"Cleared {removed_count} demo entries",
        "real_teams_kept": ["teamA"]
    }

# Data cleanup function
def clear_demo_data():
    """Clear demo data keeping only real user accounts"""
    real_teams = ["teamA"]

    # Clear demo submissions
    to_remove = []
    for sub_id, sub in submissions_db.items():
        if sub.get("teamName") not in real_teams:
            to_remove.append(sub_id)

    for sub_id in to_remove:
        del submissions_db[sub_id]

    # Clear demo users
    to_remove = []
    for team_name in users_db.keys():
        if team_name not in real_teams:
            to_remove.append(team_name)

    for team_name in to_remove:
        del users_db[team_name]

    print(f"🧹 Cleared demo data. Keeping {len(real_teams)} real teams.")
    return len(to_remove)

# Simple token validation
def get_current_user(authorization: str = Header(None)):
    """Extract user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        token = authorization.replace("Bearer ", "")

        # Check if it's a JWT token
        if "." in token and len(token.split(".")) == 3:
            try:
                # Try to decode JWT token (simple base64 decode for payload)
                parts = token.split(".")
                # Decode the payload (middle part)
                # Add padding if needed
                payload_b64 = parts[1]
                # Add padding to make it valid base64
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += "=" * padding

                payload = base64.b64decode(payload_b64)
                user_data = json.loads(payload)

                if "teamName" in user_data:
                    return {"teamName": user_data["teamName"]}
                elif "team_name" in user_data:
                    return {"teamName": user_data["team_name"]}
                else:
                    raise HTTPException(status_code=401, detail="Invalid token format")

            except Exception as e:
                print(f"JWT decode error: {e}")
                # Fall through to simple token validation

        # Simple token validation - extract team name
        if token.startswith("token_"):
            parts = token.split("_")
            if len(parts) >= 2:
                team_name = "_".join(parts[1:-1])  # Handle team names with underscores
                if not team_name:  # If team name is empty, take the last part minus timestamp
                    team_name = parts[-2] if len(parts) > 2 else parts[1]
                return {"teamName": team_name}

        raise HTTPException(status_code=401, detail="Invalid token format")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

def create_jwt_token(team_name: str, email: str) -> str:
    """Create a simple JWT-like token"""
    import time

    # Create payload
    payload = {
        "teamName": team_name,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + (24 * 60 * 60)  # 24 hours
    }

    # Simple JWT-like token (for demo purposes)
    header = {"alg": "HS256", "typ": "JWT"}

    # Encode header and payload
    header_b64 = base64.b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    # Simple signature (in production, use proper JWT signing)
    signature = "signature"

    return f"{header_b64}.{payload_b64}.{signature}"

@app.post("/api/register")
async def register_user(user: UserRegister):
    """Register a new user/team"""
    if user.teamName in users_db:
        raise HTTPException(status_code=400, detail="Team name already exists")

    # Simple password hashing (use proper hashing in production)
    users_db[user.teamName] = {
        "email": user.email,
        "password": user.password,  # In production, hash this!
        "created_at": datetime.now().isoformat(),
        "totalSubmissions": 0,
        "bestScore": 0.0
    }

    # Generate JWT token
    token = create_jwt_token(user.teamName, user.email)

    return {
        "access_token": token,
        "user": {
            "teamName": user.teamName,
            "email": user.email
        },
        "message": "User registered successfully"
    }

@app.post("/api/login")
async def login_user(user: UserLogin):
    """Login user and return token"""
    if user.teamName not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_user = users_db[user.teamName]
    if stored_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    token = create_jwt_token(user.teamName, stored_user["email"])

    return {
        "access_token": token,
        "user": {
            "teamName": user.teamName,
            "email": stored_user["email"]
        },
        "message": "Login successful"
    }

@app.post("/api/submit-to-codabench")
async def submit_algorithm(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    algorithm_name: str = Form(...),
    paper_title: str = Form(""),
    paper_authors: str = Form(""),
    paper_type: str = Form(""),
    paper_doi: str = Form(""),
    authorization: str = Header(None)
):
    """Submit algorithm for evaluation"""

    # Get current user
    current_user = get_current_user(authorization)
    team_name = current_user["teamName"]

    # Generate unique submission ID
    submission_id = str(uuid.uuid4())

    # Create submission directory
    submission_dir = UPLOAD_DIR / submission_id
    submission_dir.mkdir(exist_ok=True)

    try:
        # Validate file
        if not file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

        # Check file size (max 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 50MB)")

        # Save uploaded file
        file_path = submission_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create submission record
        submission_data = {
            "id": submission_id,
            "submission_id": submission_id,
            "teamName": team_name,
            "team_name": team_name,
            "algorithmName": algorithm_name,
            "algorithm_name": algorithm_name,
            "paper_title": paper_title,
            "paper_authors": paper_authors,
            "paper_type": paper_type,
            "paper_doi": paper_doi,
            "filename": file.filename,
            "fileName": file.filename,
            "status": "processing",
            "submission_status": "processing",
            "submitted_at": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat(),
            "file_path": str(file_path),
            "score": None,
            "metrics": None
        }

        submissions_db[submission_id] = submission_data

        # Add background task for evaluation
        background_tasks.add_task(process_submission, submission_id)

        return {
            "submission_id": submission_id,
            "status": "processing",
            "message": "Submission received and queued for evaluation"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing submission: {str(e)}")

async def process_submission(submission_id: str):
    """Background task to process submission"""
    try:
        submission = submissions_db[submission_id]
        submission["status"] = "processing"
        submission["submission_status"] = "processing"

        # Simulate evaluation process
        await asyncio.sleep(5)  # Simulate processing time

        # Run local evaluation (simplified)
        results = await run_local_evaluation(submission["file_path"])

        # Update submission with results
        submission.update({
            "status": "completed",
            "submission_status": "completed",
            "score": results.get("score", 0.0),
            "metrics": results.get("metrics", {}),
            "completed_at": datetime.now().isoformat()
        })

        # Update user stats
        team_name = submission["teamName"]
        if team_name in users_db:
            user = users_db[team_name]
            user["totalSubmissions"] = user.get("totalSubmissions", 0) + 1
            current_best = user.get("bestScore", 0)
            new_score = results.get("score", 0)
            if new_score > current_best:
                user["bestScore"] = new_score

        print(f"✅ Submission {submission_id} completed with score: {results.get('score', 0)}")

    except Exception as e:
        print(f"❌ Submission {submission_id} failed: {str(e)}")
        submission = submissions_db[submission_id]
        submission.update({
            "status": "failed",
            "submission_status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

async def run_local_evaluation(file_path: str) -> Dict[str, Any]:
    """Run local evaluation (simplified version)"""
    try:
        # Simulate evaluation results
        import random

        # Generate realistic random scores
        cr = round(random.uniform(8.0, 50.0), 1)  # Compression Ratio
        prd = round(random.uniform(0.001, 0.1), 4)  # PRD (lower is better)

        # Calculate composite score (simplified formula)
        score = round(cr * (1.0 / (prd + 0.001)) * 0.1, 1)

        return {
            "status": "completed",
            "score": score,
            "metrics": {
                "CR": cr,
                "PRD": prd,
                "Score": score,
                "RMSE": round(random.uniform(0.01, 0.1), 4),
                "SNR": round(random.uniform(15.0, 30.0), 1)
            },
            "evaluation_time": round(random.uniform(2.0, 10.0), 2)
        }
    except Exception as e:
        return {
            "status": "failed",
            "score": 0.0,
            "error": str(e),
            "metrics": {}
        }

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get current leaderboard"""
    try:
        # Get all completed submissions
        completed_submissions = [
            sub for sub in submissions_db.values()
            if sub.get("status") == "completed" and sub.get("score", 0) > 0
        ]

        # Group by team and get best score for each
        team_best = {}
        for sub in completed_submissions:
            team_name = sub.get("teamName")
            score = float(sub.get("score", 0))

            if team_name not in team_best or score > team_best[team_name]["score"]:
                team_best[team_name] = {
                    "participant_name": team_name,
                    "score": score,
                    "scores": {
                        "Score": score,
                        "CR": sub.get("metrics", {}).get("CR", 0),
                        "PRD": sub.get("metrics", {}).get("PRD", 0)
                    },
                    "submission_date": sub.get("submitted_at", ""),
                    "algorithm_name": sub.get("algorithmName", "")
                }

        # Convert to list and sort by score
        results = list(team_best.values())
        results.sort(key=lambda x: x["score"], reverse=True)

        return {"results": results}

    except Exception as e:
        print(f"❌ Leaderboard error: {str(e)}")
        return {"results": []}

@app.get("/api/submission-status/{submission_id}")
async def get_submission_status(submission_id: str):
    """Get status of a specific submission"""
    if submission_id not in submissions_db:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission = submissions_db[submission_id]
    return {
        "submission_id": submission_id,
        "status": submission.get("status", "unknown"),
        "score": submission.get("score"),
        "metrics": submission.get("metrics", {}),
        "submitted_at": submission.get("submitted_at"),
        "error": submission.get("error")
    }

@app.get("/api/user-submissions/{team_name}")
async def get_user_submissions(
    team_name: str,
    authorization: str = Header(None)
):
    """Get submissions for a specific team"""
    current_user = get_current_user(authorization)

    # Users can only access their own submissions
    if current_user["teamName"] != team_name:
        raise HTTPException(status_code=403, detail="Access denied")

    user_submissions = [
        sub for sub in submissions_db.values()
        if sub.get("teamName") == team_name
    ]

    # Sort by submission time (newest first)
    user_submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)

    return {"submissions": user_submissions}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "ECG Compression Challenge Backend is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "total_submissions": len(submissions_db),
        "active_users": len(users_db)
    }

@app.get("/api/test-codabench")
async def test_codabench_connection():
    """Test backend connection endpoint"""
    return {
        "status": "connected",
        "message": "Backend connection successful",
        "competitionId": "ecg-compression-challenge",
        "timestamp": datetime.now().isoformat(),
        "backend_version": "1.0.0"
    }

@app.post("/api/admin/clear-demo-data")
async def clear_demo_data_endpoint():
    """Admin endpoint to clear demo data"""
    removed_count = clear_demo_data()
    return {
        "status": "success",
        "message": f"Cleared {removed_count} demo entries",
        "real_teams_kept": ["teamA"],
        "remaining_users": len(users_db),
        "remaining_submissions": len(submissions_db)
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ECG Compression Challenge Backend",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ECG Compression Challenge Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )