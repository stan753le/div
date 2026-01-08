"""
Init script to create a local SQLite DB from the coursea_data.csv file.

The coursea_data.csv has this structure:
- (index column)
- course_title
- course_organization
- course_Certificate_type
- course_rating
- course_difficulty
- course_students_enrolled

This script maps the CSV to our programs table structure with:
- id (auto-generated UUID)
- name (from course_title)
- description (from course_organization + certificate type)
- tags (extracted from course_title and organization)
- skills (generated from course content)
- requirements (based on difficulty and rating)

Run: `python backend/init_db.py` (ensure `pandas` is installed)
"""
import os
import sqlite3
import uuid
from pathlib import Path
import pandas as pd
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SQLITE_DB_PATH", BACKEND / "data.db"))


def extract_tags_from_title(title: str) -> list:
    """Extract relevant tags from course title."""
    common_topics = [
        'python', 'java', 'programming', 'data', 'science', 'machine learning',
        'ai', 'security', 'web', 'mobile', 'cloud', 'business', 'marketing',
        'finance', 'management', 'design', 'art', 'engineering', 'math',
        'statistics', 'analytics', 'development', 'leadership', 'strategy'
    ]

    title_lower = title.lower()
    tags = []

    for topic in common_topics:
        if topic in title_lower:
            tags.append(topic)

    if 'deep learning' in title_lower or 'neural' in title_lower:
        tags.extend(['deep learning', 'neural networks'])
    if 'database' in title_lower or 'sql' in title_lower:
        tags.extend(['database', 'sql'])
    if 'iot' in title_lower or 'internet of things' in title_lower:
        tags.append('iot')

    return list(set(tags))[:10]


def extract_skills_from_course(title: str, org: str, cert_type: str) -> list:
    """Generate skills list based on course content."""
    skills = []

    title_lower = title.lower()

    if 'python' in title_lower:
        skills.extend(['Python programming', 'Data analysis'])
    if 'java' in title_lower:
        skills.extend(['Java programming', 'Object-oriented design'])
    if 'data science' in title_lower:
        skills.extend(['Statistical analysis', 'Data visualization', 'Machine learning'])
    if 'machine learning' in title_lower or 'ml' in title_lower:
        skills.extend(['Machine learning algorithms', 'Model training', 'Feature engineering'])
    if 'business' in title_lower:
        skills.extend(['Business strategy', 'Decision making', 'Analysis'])
    if 'marketing' in title_lower:
        skills.extend(['Marketing strategy', 'Campaign management', 'Customer analysis'])
    if 'design' in title_lower:
        skills.extend(['Design thinking', 'Creative problem solving', 'User experience'])
    if 'web' in title_lower:
        skills.extend(['HTML/CSS', 'JavaScript', 'Web development'])
    if 'security' in title_lower or 'cybersecurity' in title_lower:
        skills.extend(['Security analysis', 'Risk management', 'Network security'])
    if 'cloud' in title_lower:
        skills.extend(['Cloud computing', 'Infrastructure management', 'DevOps'])

    if cert_type == 'SPECIALIZATION':
        skills.append('Comprehensive knowledge')
    if cert_type == 'PROFESSIONAL CERTIFICATE':
        skills.append('Professional certification')

    return list(set(skills))[:6]


def map_coursea_to_programs(csv_path: Path) -> pd.DataFrame:
    """Map coursea_data.csv to programs table structure."""
    df = pd.read_csv(csv_path)

    programs = []

    for _, row in df.iterrows():
        program_id = str(uuid.uuid4())
        title = str(row.get('course_title', 'Untitled Course'))
        org = str(row.get('course_organization', 'Unknown'))
        cert_type = str(row.get('course_Certificate_type', 'COURSE'))
        rating = row.get('course_rating', 4.5)
        difficulty = str(row.get('course_difficulty', 'Beginner'))
        enrolled = str(row.get('course_students_enrolled', '0'))

        description = f"Offered by {org}. {cert_type.title()} with {enrolled} students enrolled. "
        description += f"This comprehensive program covers essential concepts and practical skills."

        tags = extract_tags_from_title(title)
        if difficulty.lower() in ['beginner', 'intermediate', 'advanced', 'mixed']:
            tags.append(difficulty.lower())

        skills = extract_skills_from_course(title, org, cert_type)

        requirements = {
            "min_grade": 65 if difficulty.lower() == 'beginner' else 70 if difficulty.lower() == 'intermediate' else 75,
            "difficulty": difficulty,
            "rating": float(rating) if pd.notna(rating) else 4.5
        }

        programs.append({
            'id': program_id,
            'name': title,
            'description': description,
            'tags': json.dumps(tags),
            'skills': json.dumps(skills),
            'requirements': json.dumps(requirements)
        })

    return pd.DataFrame(programs)


def main():
    print(f"Initializing SQLite DB at {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        print(f"Removing existing database at {DB_PATH}")
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    coursea_csv = ROOT / "coursea_data.csv"

    if not coursea_csv.exists():
        print(f"ERROR: coursea_data.csv not found at {coursea_csv}")
        print("Please ensure the file exists in the project root.")
        return

    print(f"Loading coursea_data.csv from {coursea_csv}")
    programs_df = map_coursea_to_programs(coursea_csv)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS programs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            skills TEXT,
            requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for _, row in programs_df.iterrows():
        cur.execute("""
            INSERT INTO programs (id, name, description, tags, skills, requirements)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (row['id'], row['name'], row['description'], row['tags'], row['skills'], row['requirements']))

    print(f"✅ Created 'programs' table with {len(programs_df)} courses")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            interests TEXT,
            grades TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created 'students' table")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            program_id TEXT,
            clicked INTEGER DEFAULT 0,
            accepted INTEGER DEFAULT 0,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (program_id) REFERENCES programs(id)
        )
    """)
    print("✅ Created 'feedback' table")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            program_id TEXT,
            score REAL,
            explanation TEXT,
            algorithm TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (program_id) REFERENCES programs(id)
        )
    """)
    print("✅ Created 'recommendations' table")

    conn.commit()
    conn.close()

    print(f"\n✅ SQLite database initialized successfully at {DB_PATH}")
    print(f"   Programs loaded: {len(programs_df)}")
    print("\nTo use SQLite mode, set environment variable: USE_SQLITE=true")


if __name__ == "__main__":
    main()
