#!/usr/bin/env python3
"""
Step-by-step verification script for Sentilytics 360 project
This script checks if all components are properly configured and can run.
"""

import sys
import os

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def check_python_version():
    print_step(1, "Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERROR] ERROR: Python 3.8+ is required")
        return False
        print("[OK] Python version is compatible")
    return True

def check_imports():
    print_step(2, "Checking Critical Imports")
    issues = []
    
    # Core dependencies
    try:
        import fastapi
        print("[OK] fastapi")
    except ImportError as e:
        issues.append(f"[ERROR] fastapi: {e}")
        print(f"[ERROR] fastapi: {e}")
    
    try:
        import uvicorn
        print("[OK] uvicorn")
    except ImportError as e:
        issues.append(f"[ERROR] uvicorn: {e}")
        print(f"[ERROR] uvicorn: {e}")
    
    try:
        import pandas
        print("[OK] pandas")
    except ImportError as e:
        issues.append(f"[ERROR] pandas: {e}")
        print(f"[ERROR] pandas: {e}")
    
    try:
        import sqlalchemy
        print("[OK] sqlalchemy")
    except ImportError as e:
        issues.append(f"[ERROR] sqlalchemy: {e}")
        print(f"[ERROR] sqlalchemy: {e}")
    
    try:
        import transformers
        print("[OK] transformers")
    except ImportError as e:
        issues.append(f"[ERROR] transformers: {e}")
        print(f"[ERROR] transformers: {e}")
    
    try:
        import nltk
        print("[OK] nltk")
    except ImportError as e:
        issues.append(f"[ERROR] nltk: {e}")
        print(f"[ERROR] nltk: {e}")
    
    try:
        import praw
        print("[OK] praw")
    except ImportError as e:
        issues.append(f"[ERROR] praw: {e}")
        print(f"[ERROR] praw: {e}")
    
    # Check ntscraper (might not be in requirements)
    try:
        import ntscraper
        print("[OK] ntscraper")
    except ImportError as e:
        issues.append(f"[WARNING]  ntscraper: {e} (Used in api_clients.py but may not be in requirements.txt)")
        print(f"[WARNING]  ntscraper: {e} (Used in api_clients.py but may not be in requirements.txt)")
    
    return len(issues) == 0, issues

def check_project_structure():
    print_step(3, "Checking Project Structure")
    required_files = [
        "app.py",
        "requirements.txt",
        "database/db.py",
        "database/models.py",
        "src/processing/pipeline.py",
        "src/processing/text_cleaner.py",
        "src/connectors/api_clients.py",
        "src/analysis/model.py",
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            missing.append(file)
            print(f"[ERROR] {file} - MISSING")
    
    return len(missing) == 0, missing

def check_imports_in_code():
    print_step(4, "Checking Code Imports")
    issues = []
    
    # Test database imports
    try:
        from database.db import engine, get_db
        print("[OK] database.db imports")
    except Exception as e:
        issues.append(f"database.db: {e}")
        print(f"[ERROR] database.db: {e}")
    
    try:
        from database import models
        print("[OK] database.models imports")
    except Exception as e:
        issues.append(f"database.models: {e}")
        print(f"[ERROR] database.models: {e}")
    
    # Test pipeline imports
    try:
        from src.processing.pipeline import run_sentiment_pipeline
        print("[OK] src.processing.pipeline imports")
    except Exception as e:
        issues.append(f"src.processing.pipeline: {e}")
        print(f"[ERROR] src.processing.pipeline: {e}")
    
    # Test connector imports
    try:
        from src.connectors.api_clients import fetch_twitter_data, fetch_reddit_data
        print("[OK] src.connectors.api_clients imports")
    except Exception as e:
        issues.append(f"src.connectors.api_clients: {e}")
        print(f"[ERROR] src.connectors.api_clients: {e}")
    
    # Test analysis imports
    try:
        from src.analysis.model import get_analyzer
        print("[OK] src.analysis.model imports")
    except Exception as e:
        issues.append(f"src.analysis.model: {e}")
        print(f"[ERROR] src.analysis.model: {e}")
    
    return len(issues) == 0, issues

def check_database_setup():
    print_step(5, "Checking Database Setup")
    try:
        from database.db import engine, Base
        from database import models
        
        # Check if tables can be created
        Base.metadata.create_all(bind=engine)
        print("[OK] Database engine created")
        print("[OK] Database tables can be created")
        return True, []
    except Exception as e:
        print(f"[ERROR] Database setup error: {e}")
        return False, [str(e)]

def check_environment_variables():
    print_step(6, "Checking Environment Variables")
    from dotenv import load_dotenv
    load_dotenv()
    
    twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    print(f"TWITTER_BEARER_TOKEN: {'[OK] Set' if twitter_token else '[WARNING]  Not set (optional if using ntscraper)'}")
    print(f"REDDIT_CLIENT_ID: {'[OK] Set' if reddit_client_id else '[WARNING]  Not set'}")
    print(f"REDDIT_CLIENT_SECRET: {'[OK] Set' if reddit_secret else '[WARNING]  Not set'}")
    
    if not reddit_client_id or not reddit_secret:
        return False, ["Reddit credentials not set (required for Reddit data)"]
    
    return True, []

def check_fastapi_app():
    print_step(7, "Checking FastAPI Application")
    try:
        # Import app but don't run it
        import sys
        sys.path.insert(0, os.getcwd())
        from main import app
        print("[OK] FastAPI app can be imported")
        print(f"[OK] App title: {app.title}")
        print(f"[OK] App version: {app.version}")
        return True, []
    except Exception as e:
        print(f"[ERROR] FastAPI app error: {e}")
        import traceback
        traceback.print_exc()
        return False, [str(e)]

def check_missing_dependencies():
    print_step(8, "Checking for Missing Dependencies in requirements.txt")
    issues = []
    
    # Check if ntscraper is in requirements
    with open("requirements.txt", "r") as f:
        requirements = f.read()
        if "ntscraper" not in requirements.lower():
            issues.append("ntscraper is used in api_clients.py but not in requirements.txt")
            print("[WARNING]  ntscraper not found in requirements.txt (but used in code)")
        else:
            print("[OK] ntscraper found in requirements.txt")
    
    return len(issues) == 0, issues

def main():
    print("\n" + "="*60)
    print("SENTILYTICS 360 - PROJECT VERIFICATION")
    print("="*60)
    
    all_checks_passed = True
    all_issues = []
    
    # Step 1: Python version
    if not check_python_version():
        all_checks_passed = False
        return
    
    # Step 2: Check imports
    passed, issues = check_imports()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 3: Project structure
    passed, issues = check_project_structure()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 4: Code imports
    passed, issues = check_imports_in_code()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 5: Database setup
    passed, issues = check_database_setup()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 6: Environment variables
    passed, issues = check_environment_variables()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 7: FastAPI app
    passed, issues = check_fastapi_app()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Step 8: Missing dependencies
    passed, issues = check_missing_dependencies()
    if not passed:
        all_checks_passed = False
        all_issues.extend(issues)
    
    # Final summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    if all_checks_passed:
        print("[OK] ALL CHECKS PASSED!")
        print("\nYour project should be ready to run!")
        print("\nTo start the backend:")
        print("  uvicorn app:app --reload --port 8000")
        print("\nTo start the frontend:")
        print("  cd frontend && npm start")
    else:
        print("[ERROR] SOME ISSUES FOUND:")
        for issue in all_issues:
            print(f"  - {issue}")
        print("\n[WARNING]  Please fix these issues before running the project.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

