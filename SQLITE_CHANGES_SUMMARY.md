# SQLite Implementation Summary

## What Was Changed

The Study Program Recommender System has been modified to work with SQLite and the coursea_data.csv file structure instead of requiring Supabase.

## Changes Made

### 1. Database Initialization Script (`backend/init_db.py`)

**Complete rewrite** to handle coursea_data.csv structure:

- **CSV Parsing**: Reads coursea_data.csv with columns:
  - course_title
  - course_organization
  - course_Certificate_type
  - course_rating
  - course_difficulty
  - course_students_enrolled

- **Intelligent Mapping**:
  - Extracts tags from course titles (programming, data science, AI, etc.)
  - Generates relevant skills based on course content
  - Creates appropriate requirements based on difficulty level
  - Builds comprehensive descriptions

- **Database Schema**:
  - Creates proper SQLite tables matching Supabase structure
  - Stores JSON fields (tags, skills, requirements) as TEXT
  - Adds foreign key constraints

**Result**: 499 courses automatically loaded and mapped to the recommendation system format

### 2. SQLite Adapter (`backend/app/sqlite_adapter.py`)

**Enhanced** with JSON field handling:

- **Automatic JSON Parsing**: When reading from database, automatically converts JSON strings to Python objects for:
  - programs: tags, skills, requirements
  - students: interests, grades

- **Automatic JSON Serialization**: When writing to database, converts Python objects to JSON strings

- **UUID Generation**: Automatically generates IDs for new records

- **Supabase-Compatible API**: Maintains the same interface so no code changes needed elsewhere

### 3. Configuration (`backend/app/config.py`)

**Updated** to support extra environment variables:

- Added `extra="ignore"` to Pydantic config
- Prevents validation errors when USE_SQLITE is in .env
- Maintains backward compatibility with Supabase

### 4. Environment Configuration (`backend/.env`)

**Created** with SQLite settings:

```bash
USE_SQLITE=true
SQLITE_DB_PATH=data.db
```

### 5. Documentation

**Added comprehensive guides**:

- **SQLITE_SETUP.md**: Full setup and usage guide
- **SQLITE_CHANGES_SUMMARY.md**: This document
- **start_sqlite.sh**: Quick start script

### 6. Test Script (`backend/test_sqlite.py`)

**Created** to verify SQLite functionality:
- Tests database connection
- Verifies JSON parsing
- Shows sample data

## How It Works

### Data Flow

```
coursea_data.csv
    ↓
init_db.py extracts/maps data
    ↓
SQLite database (data.db)
    ↓
sqlite_adapter.py (mimics Supabase API)
    ↓
Recommendation system (unchanged)
```

### Tag Extraction Example

For a course titled "Python for Data Science":
- **Extracted tags**: `['python', 'data', 'science', 'programming']`
- **Generated skills**: `['Python programming', 'Data analysis', 'Statistical analysis', 'Data visualization', 'Machine learning']`
- **Requirements**: `{"min_grade": 65, "difficulty": "Beginner", "rating": 4.7}`

### JSON Storage

Data is stored in SQLite as JSON strings but automatically converted:

**In Database (TEXT)**:
```
tags = '["python", "data", "science"]'
```

**In Application (list)**:
```python
program['tags']  # ['python', 'data', 'science']
```

## Files Modified

1. `backend/init_db.py` - Complete rewrite
2. `backend/app/sqlite_adapter.py` - Enhanced with JSON handling
3. `backend/app/config.py` - Updated Pydantic config
4. `backend/.env` - Created with SQLite settings

## Files Created

1. `SQLITE_SETUP.md` - Setup guide
2. `SQLITE_CHANGES_SUMMARY.md` - This file
3. `backend/test_sqlite.py` - Test script
4. `start_sqlite.sh` - Quick start script
5. `backend/data.db` - SQLite database (generated)

## Quick Start

### Option 1: Using the Script

```bash
./start_sqlite.sh
```

### Option 2: Manual Steps

```bash
# Initialize database
cd backend
python3 init_db.py

# Start backend
export USE_SQLITE=true
export SQLITE_DB_PATH=data.db
python3 -m uvicorn app.main:app --reload

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

## Verification

After initialization, you should see:

```bash
✅ SQLite database initialized successfully at backend/data.db
   Programs loaded: 499
```

Test the setup:

```bash
cd backend
python3 test_sqlite.py
```

Expected output:

```
Total programs: 499

First 3 programs:
1. (ISC)² Systems Security Certified Practitioner (SSCP)
   Tags: ['security', 'beginner']
   Skills: ['Risk management', 'Network security']
   ...

✅ SQLite database is working correctly!
```

## API Endpoints Work Unchanged

All API endpoints function identically:

- `POST /students` - Create student profile
- `POST /recommendations` - Get recommendations
- `POST /feedback` - Submit feedback
- `GET /programs` - List all programs
- `GET /analytics/*` - Analytics endpoints

## Advantages of SQLite Mode

1. **Zero External Dependencies**: No Supabase account needed
2. **Offline Development**: Works completely offline
3. **Simple Deployment**: Single database file
4. **Fast Setup**: Database ready in seconds
5. **Easy Backup**: Just copy data.db file
6. **Local Testing**: Perfect for development
7. **Direct CSV Integration**: Automatic mapping from coursea_data.csv

## Switching Between Modes

### SQLite Mode (Current)
```bash
# In backend/.env
USE_SQLITE=true
```

### Supabase Mode
```bash
# In backend/.env
USE_SQLITE=false
SUPABASE_URL=your_actual_url
SUPABASE_ANON_KEY=your_actual_key
```

No code changes needed - just change the environment variable!

## Database Schema

### programs
```sql
CREATE TABLE programs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tags TEXT,           -- JSON array as string
    skills TEXT,         -- JSON array as string
    requirements TEXT,   -- JSON object as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### students
```sql
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    interests TEXT,      -- JSON array as string
    grades TEXT,         -- JSON object as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### feedback, recommendations
Same structure as Supabase version

## Performance Notes

- **SQLite**: Excellent for development, testing, and small deployments (< 100k courses)
- **Read Performance**: Very fast, all queries cached in memory
- **Write Performance**: Good for single-user, adequate for small teams
- **Scalability**: For production with many concurrent users, consider PostgreSQL/Supabase

## Troubleshooting

### Issue: Module not found errors
**Solution**: Install dependencies
```bash
pip install --break-system-packages pandas pydantic pydantic-settings python-dotenv scikit-learn scipy
```

### Issue: Database file not found
**Solution**: Run init_db.py from backend directory
```bash
cd backend
python3 init_db.py
```

### Issue: Validation error for USE_SQLITE
**Solution**: This is now fixed - config.py ignores extra env variables

### Issue: JSON fields showing as strings
**Solution**: Ensure you're using the updated sqlite_adapter.py that auto-parses JSON

## Next Steps

1. Start the application with `./start_sqlite.sh`
2. Open browser to `http://localhost:8000/docs` to test API
3. Create student profiles and test recommendations
4. See SQLITE_SETUP.md for detailed usage

## Summary

The system now works seamlessly with SQLite and coursea_data.csv:

- Automatic CSV parsing and intelligent data mapping
- JSON fields handled transparently
- Same API and functionality as Supabase version
- 499 courses ready to use
- Perfect for development and testing
- Easy to switch back to Supabase when needed

All recommendation algorithms (content-based, collaborative filtering, hybrid, cold-start) work identically in SQLite mode!
