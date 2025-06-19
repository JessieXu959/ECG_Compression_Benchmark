"""
FastAPI Backend for ECG Compression Challenge
Provides REST API endpoints for user management, file submission, and leaderboard
"""

import os
import uuid
import shutil
import json
import time
import zipfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import our custom modules
from storage import (
    save_user, get_user, get_all_users, save_submission, get_submissions,
    update_submission_status, get_user_submissions, get_leaderboard,
    delete_user_data
)
from evaluate import evaluate_submission_async

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "ecg-compression-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
UPLOAD_MAX_SIZE = int(os.getenv("UPLOAD_MAX_SIZE", "100")) * 1024 * 1024  # MB to bytes

# Directories
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp")
SCORING_DIR = Path("scoring")
DATA_DIR = Path("data")

# Create directories
for directory in [UPLOAD_DIR, TEMP_DIR, SCORING_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="ECG Compression Challenge API",
    description="Backend API for ECG compression algorithm submissions and evaluation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class UserRegister(BaseModel):
    teamName: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    teamName: str
    password: str

class SubmissionResponse(BaseModel):
    submission_id: str
    message: str
    status: str

class LeaderboardEntry(BaseModel):
    participant_name: str
    score: float
    scores: Dict[str, float]
    submission_date: str
    algorithm_name: str

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        team_name: str = payload.get("sub")
        if team_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(team_name)
    if user is None:
        raise credentials_exception

    return user

def generate_submission_id() -> str:
    """Generate unique submission ID"""
    return str(uuid.uuid4())

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# API Endpoints

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    """Register a new user"""

    # Check if user already exists
    existing_user = get_user(user.teamName)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already registered"
        )

    # Hash password and save user
    hashed_password = get_password_hash(user.password)
    user_data = {
        'teamName': user.teamName,
        'email': user.email,
        'password': hashed_password,
        'registeredDate': datetime.utcnow().isoformat(),
        'totalSubmissions': 0,
        'bestScore': 0.0
    }

    save_user(user.teamName, user_data)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.teamName}, expires_delta=access_token_expires
    )

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "teamName": user.teamName,
            "email": user.email
        }
    }

@app.post("/api/login")
async def login_user(user: UserLogin):
    """Authenticate user and return access token"""

    # Get user from storage
    stored_user = get_user(user.teamName)
    if not stored_user or not verify_password(user.password, stored_user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect team name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.teamName}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "teamName": stored_user['teamName'],
            "email": stored_user['email']
        }
    }

@app.get("/api/users")
async def get_all_users_endpoint():
    """Get all registered users (without passwords)"""
    users = get_all_users()
    return {
        "users": users,
        "total": len(users)
    }

@app.post("/api/submit-to-codabench", response_model=SubmissionResponse)
async def submit_algorithm(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    algorithm_name: str = Form(...),
    paper_title: str = Form(""),
    paper_authors: str = Form(""),
    paper_type: str = Form(""),
    paper_doi: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Submit algorithm ZIP file for evaluation"""

    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only ZIP files are allowed"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > UPLOAD_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {UPLOAD_MAX_SIZE // (1024*1024)}MB"
        )
    await file.seek(0)  # Reset file pointer

    # Generate submission ID and save file
    submission_id = generate_submission_id()
    upload_path = UPLOAD_DIR / f"{submission_id}_{file.filename}"

    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Calculate file hash for integrity
    file_hash = calculate_file_hash(str(upload_path))

    # Save submission metadata
    submission_data = {
        'id': submission_id,
        'teamName': current_user['teamName'],
        'algorithmName': algorithm_name,
        'fileName': file.filename,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'processing',
        'score': None,
        'metrics': {},
        'filePath': str(upload_path),
        'fileHash': file_hash,
        'paperTitle': paper_title,
        'paperAuthors': paper_authors,
        'paperType': paper_type,
        'paperDOI': paper_doi,
        'evaluationTime': None
    }

    save_submission(submission_id, submission_data)

    # Start background evaluation
    background_tasks.add_task(
        evaluate_submission_background,
        str(upload_path),
        submission_id
    )

    return SubmissionResponse(
        submission_id=submission_id,
        message="Submission received and queued for evaluation",
        status="processing"
    )

async def evaluate_submission_background(zip_path: str, submission_id: str):
    """Background task for submission evaluation"""
    try:
        # Run evaluation
        result = evaluate_submission_async(zip_path, submission_id)

        # Update submission with results
        update_data = {
            'score': result.get('score', 0.0),
            'metrics': result.get('metrics', {}),
            'evaluationTime': result.get('evaluation_time', 0.0)
        }

        final_status = result.get('status', 'failed')
        if final_status == 'completed':
            final_status = 'completed'
        else:
            final_status = 'failed'
            update_data['error'] = result.get('error', 'Unknown error')

        update_submission_status(submission_id, final_status, update_data)

        # Update user's best score if needed
        submission_data = next(
            (s for s in get_submissions() if s['id'] == submission_id),
            None
        )
        if submission_data and final_status == 'completed':
            user = get_user(submission_data['teamName'])
            if user:
                current_best = float(user.get('bestScore', 0))
                new_score = float(result.get('score', 0))
                if new_score > current_best:
                    user_data = user.copy()
                    user_data['bestScore'] = new_score
                    save_user(submission_data['teamName'], user_data)

                # Update total submissions count
                user_data = get_user(submission_data['teamName'])
                if user_data:
                    user_data['totalSubmissions'] = int(user_data.get('totalSubmissions', 0)) + 1
                    save_user(submission_data['teamName'], user_data)

    except Exception as e:
        # Update submission with error
        update_submission_status(
            submission_id,
            'failed',
            {'error': str(e)}
        )

    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except OSError:
            pass  # File might already be deleted

@app.get("/api/leaderboard")
async def get_leaderboard_endpoint():
    """Get current leaderboard"""
    leaderboard = get_leaderboard(limit=50)
    return {"results": leaderboard}

@app.get("/api/submission-status/{submission_id}")
async def get_submission_status(submission_id: str):
    """Get status of a specific submission"""
    submissions = get_submissions()
    submission = next((s for s in submissions if s['id'] == submission_id), None)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    return {
        "submission_id": submission_id,
        "status": submission['status'],
        "score": submission.get('score'),
        "metrics": submission.get('metrics', {}),
        "timestamp": submission.get('timestamp'),
        "error": submission.get('error')
    }

@app.get("/api/user-submissions/{team_name}")
async def get_user_submissions_endpoint(
    team_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get submissions for a specific user"""

    # Users can only access their own submissions
    if current_user['teamName'] != team_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    user_submissions = get_user_submissions(team_name)
    return {"submissions": user_submissions}

@app.get("/api/global-stats")
async def get_global_stats():
    """Get global performance statistics for the homepage metrics"""
    try:
        # Get all completed submissions
        submissions = get_submissions()
        completed_submissions = [
            sub for sub in submissions
            if sub.get("status") == "completed" and float(sub.get("score", 0)) > 0
        ]

        if not completed_submissions:
            # Return default values when no submissions exist
            return {
                "topCompressionRatio": {
                    "value": "N/A",
                    "team": "No submissions yet"
                },
                "bestPRD": {
                    "value": "N/A",
                    "team": "No submissions yet"
                },
                "averageScore": "N/A",
                "activeTeams": 0,
                "totalSubmissions": 0
            }

        # Calculate metrics
        best_cr = 0
        best_cr_team = ""
        best_prd = float('inf')
        best_prd_team = ""
        total_score = 0
        team_names = set()

        for sub in completed_submissions:
            team_names.add(sub.get('teamName', 'Unknown'))
            metrics = sub.get('metrics', {})
            score = float(sub.get('score', 0))
            total_score += score

            # Track best compression ratio
            cr = float(metrics.get('CR', 0))
            if cr > best_cr:
                best_cr = cr
                best_cr_team = sub.get('teamName', 'Unknown')

            # Track best PRD (lowest is best)
            prd = float(metrics.get('PRD', float('inf')))
            if prd < best_prd:
                best_prd = prd
                best_prd_team = sub.get('teamName', 'Unknown')

        # Calculate average score
        avg_score = total_score / len(completed_submissions) if completed_submissions else 0

        # Format the response
        return {
            "topCompressionRatio": {
                "value": f"{best_cr:.1f}:1" if best_cr > 0 else "N/A",
                "team": best_cr_team if best_cr > 0 else "No submissions yet"
            },
            "bestPRD": {
                "value": f"{best_prd:.3f}%" if best_prd != float('inf') else "N/A",
                "team": best_prd_team if best_prd != float('inf') else "No submissions yet"
            },
            "averageScore": f"{avg_score:.3f}" if avg_score > 0 else "N/A",
            "activeTeams": len(team_names),
            "totalSubmissions": len(completed_submissions)
        }

    except Exception as e:
        print(f"❌ Global stats error: {str(e)}")
        return {
            "topCompressionRatio": {
                "value": "Error",
                "team": "System error"
            },
            "bestPRD": {
                "value": "Error",
                "team": "System error"
            },
            "averageScore": "Error",
            "activeTeams": 0,
            "totalSubmissions": 0
        }

@app.delete("/api/user/{team_name}")
async def delete_user_account(
    team_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user account and all associated data"""

    # Users can only delete their own account
    if current_user['teamName'] != team_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Delete all user data
    delete_user_data(team_name)

    return {"message": "Account deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )