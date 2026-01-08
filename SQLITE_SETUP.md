# SQLite Setup Guide

This guide explains how to use the Study Program Recommender System with SQLite instead of Supabase, using the coursea_data.csv file.

## Overview

The system has been configured to work with SQLite as an alternative to Supabase. The coursea_data.csv file is automatically converted to the proper database structure.

## CSV Structure

The coursea_data.csv file should have these columns:
- (index column)
- course_title
- course_organization
- course_Certificate_type
- course_rating
- course_difficulty
- course_students_enrolled

## Setup Steps

### 1. Prepare the CSV File

Ensure `coursea_data.csv` exists in the project root directory:

```
project/
├── coursea_data.csv  <-- Must be here
├── backend/
├── frontend/
└── ...
```

### 2. Configure Environment

The backend is already configured to use SQLite. The `.env` file in `backend/` contains:

```bash
USE_SQLITE=true
SQLITE_DB_PATH=./backend/data.db
```

### 3. Initialize the Database

Run the initialization script to create the database from the CSV:

```bash
cd backend
python init_db.py
```

This will:
- Read coursea_data.csv
- Create a SQLite database at `backend/data.db`
- Map CSV columns to the programs table structure:
  - `course_title` → `name`
  - Course info → `description`
  - Extracted keywords → `tags` (as JSON array)
  - Generated skills → `skills` (as JSON array)
  - Difficulty/rating → `requirements` (as JSON object)
- Create empty tables for students, feedback, and recommendations

### 4. Verify the Database

Check that the database was created successfully:

```bash
sqlite3 backend/data.db "SELECT COUNT(*) FROM programs;"
```

You should see the number of courses loaded.

### 5. Start the Application

Run the backend server:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the frontend (in a separate terminal):

```bash
cd frontend
npm install
npm run dev
```

## How It Works

### Data Mapping

The init_db.py script intelligently maps coursea data to the recommendation system:

**Tags Extraction**:
- Scans course titles for keywords (python, java, data science, machine learning, etc.)
- Adds difficulty level as a tag
- Stores as JSON array

**Skills Generation**:
- Analyzes course title and type to generate relevant skills
- Examples: "Python programming", "Statistical analysis", "Machine learning"
- Stores as JSON array

**Requirements**:
- Minimum grade based on difficulty (Beginner: 65, Intermediate: 70, Advanced: 75)
- Includes difficulty level and course rating
- Stores as JSON object

**Description**:
- Combines organization, certificate type, and enrollment count
- Adds generic course description

### Database Schema

```sql
CREATE TABLE programs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tags TEXT,           -- JSON array
    skills TEXT,         -- JSON array
    requirements TEXT,   -- JSON object
    created_at TIMESTAMP
);

CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    interests TEXT,      -- JSON array
    grades TEXT,         -- JSON object
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE feedback (
    id TEXT PRIMARY KEY,
    student_id TEXT,
    program_id TEXT,
    clicked INTEGER,
    accepted INTEGER,
    rating INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE recommendations (
    id TEXT PRIMARY KEY,
    student_id TEXT,
    program_id TEXT,
    score REAL,
    explanation TEXT,
    algorithm TEXT,
    created_at TIMESTAMP
);
```

### SQLite Adapter

The `sqlite_adapter.py` provides a Supabase-compatible interface:

- Mimics Supabase's `table().select().eq().execute()` API
- Automatically parses JSON fields (tags, skills, requirements, interests, grades)
- Auto-generates UUIDs for new records
- Handles JSON serialization on insert/update

## Testing

### 1. Test Database Connection

```python
from app.database import supabase

result = supabase.table("programs").select("*").limit(5).execute()
print(f"Found {len(result.data)} programs")
for prog in result.data:
    print(f"- {prog['name']}")
    print(f"  Tags: {prog['tags']}")
    print(f"  Skills: {prog['skills']}")
```

### 2. Test Recommendations

Create a student profile and request recommendations through the API:

```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Student",
    "email": "test@example.com",
    "interests": ["programming", "data", "python"],
    "grades": {"math": 85, "computer science": 90}
  }'
```

Then get recommendations:

```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "<student_id_from_above>",
    "top_k": 5
  }'
```

## Switching Back to Supabase

To switch back to Supabase:

1. Edit `backend/.env`:
   ```bash
   USE_SQLITE=false
   SUPABASE_URL=your_actual_url
   SUPABASE_ANON_KEY=your_actual_key
   ```

2. Restart the backend server

## Troubleshooting

### Database not found
```
ERROR: coursea_data.csv not found
```
**Solution**: Place coursea_data.csv in the project root directory

### JSON parsing errors
```
JSON decode error in tags/skills
```
**Solution**: Re-run `python backend/init_db.py` to regenerate the database

### Import errors
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install dependencies: `pip install -r backend/requirements.txt`

### Permission errors
```
PermissionError: [Errno 13] Permission denied: 'backend/data.db'
```
**Solution**: Close any programs using the database file, or delete it and regenerate

## Performance Notes

SQLite is well-suited for:
- Development and testing
- Small to medium datasets (up to 100k courses)
- Single-user scenarios
- Local deployments

For production with multiple concurrent users, consider using Supabase or PostgreSQL.

## Data Management

### Adding More Courses

1. Update coursea_data.csv with new courses
2. Re-run: `python backend/init_db.py`
3. Restart the backend server

### Backup Database

```bash
cp backend/data.db backend/data.db.backup
```

### Reset Database

```bash
rm backend/data.db
python backend/init_db.py
```

## Summary

The SQLite configuration allows you to:
- Use the coursea_data.csv structure directly
- Automatically generate tags and skills from course titles
- Maintain full recommendation system functionality
- Develop and test without Supabase dependency
- Deploy the system locally with zero external dependencies

The system intelligently transforms Coursera course data into the format needed for personalized program recommendations.
