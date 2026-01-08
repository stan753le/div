# Quick Start: SQLite Mode

## System is ready to use with coursea_data.csv!

### What's Been Done

The system has been configured to use SQLite with your coursea_data.csv file (499 courses loaded).

### Files You Need to Know About

1. **coursea_data.csv** (root) - Your course data
2. **backend/data.db** (generated) - SQLite database
3. **backend/.env** - Configuration (USE_SQLITE=true)
4. **SQLITE_SETUP.md** - Full documentation
5. **start_sqlite.sh** - One-command startup

### Three Ways to Start

#### Option 1: One-Command Start (Easiest)

```bash
./start_sqlite.sh
```

#### Option 2: Manual Start

```bash
# Initialize database (first time only)
cd backend
python3 init_db.py

# Start backend
python3 -m uvicorn app.main:app --reload
```

#### Option 3: With Frontend

```bash
# Terminal 1: Backend
cd backend
python3 -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### Test the System

```bash
cd backend
python3 test_sqlite.py
```

You should see:
```
Total programs: 499
✅ SQLite database is working correctly!
```

### API Documentation

Open in browser: `http://localhost:8000/docs`

### Key Endpoints

- `POST /students` - Create student
- `POST /recommendations` - Get recommendations
- `POST /feedback` - Submit feedback
- `GET /programs` - List programs

### Example: Get Recommendations

1. Create a student:
```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "interests": ["programming", "data", "python"],
    "grades": {"math": 85, "computer science": 90}
  }'
```

2. Get recommendations (use student_id from response):
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "YOUR_STUDENT_ID_HERE",
    "top_k": 5
  }'
```

### What Makes This Different

- No Supabase account needed
- Works offline
- Uses your coursea_data.csv directly
- Same powerful recommendations
- Automatic tag and skill extraction

### Data Mapping Example

**Your CSV:**
```
course_title: "Python for Data Science"
course_organization: "University"
course_difficulty: "Beginner"
```

**Automatically becomes:**
```
name: "Python for Data Science"
tags: ["python", "data", "science", "programming"]
skills: ["Python programming", "Data analysis", "Statistical analysis"]
requirements: {"min_grade": 65, "difficulty": "Beginner"}
```

### Switch to Supabase Later

Just edit `backend/.env`:
```bash
USE_SQLITE=false
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
```

### Files Created

- `backend/data.db` - SQLite database (499 courses)
- `backend/.env` - Configuration
- `start_sqlite.sh` - Startup script
- `SQLITE_SETUP.md` - Full guide
- `SQLITE_CHANGES_SUMMARY.md` - Technical details

### Troubleshooting

**Can't import pandas?**
```bash
pip install --break-system-packages pandas
```

**Database not found?**
```bash
cd backend
python3 init_db.py
```

**Port 8000 in use?**
```bash
uvicorn app.main:app --reload --port 8001
```

### Next Steps

1. Run `./start_sqlite.sh`
2. Visit `http://localhost:8000/docs`
3. Try the API endpoints
4. Read SQLITE_SETUP.md for more details

### Summary

Your Study Program Recommender System is configured and ready to go with:

- 499 courses from coursea_data.csv
- SQLite database (no external dependencies)
- All recommendation algorithms working
- Complete API documentation
- Test scripts included

Everything works just like the Supabase version, but runs entirely locally!
