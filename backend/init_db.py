"""
Init script to create a local SQLite DB from CSVs.

It looks for these CSV files (in order):
- backend/programs.csv
- backend/students.csv
- backend/interactions.csv

If `backend/programs.csv` is missing it will attempt to use
`coursea_data.csv` at the repo root as a source for programs.

Run: `python backend/init_db.py` (ensure `pandas` is installed)
"""
import os
import csv
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SQLITE_DB_PATH", BACKEND / "data.db"))


def sanitize_col(name: str) -> str:
    return name.strip().replace(' ', '_').replace('-', '_')


def create_table_from_df(conn: sqlite3.Connection, table_name: str, df: pd.DataFrame):
    df = df.fillna("")
    cols = [sanitize_col(c) for c in df.columns]
    # create with TEXT columns (simple, robust)
    col_defs = ", ".join([f"{c} TEXT" for c in cols])
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    cur.execute(f"CREATE TABLE {table_name} ({col_defs})")
    placeholders = ",".join(["?" for _ in cols])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
    values = [tuple(str(x) for x in row) for row in df.to_numpy()]
    cur.executemany(insert_sql, values)
    conn.commit()


def main():
    print(f"Initializing SQLite DB at {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # 1) Programs
    programs_csv = BACKEND / "programs.csv"
    if not programs_csv.exists():
        # fallback to root `coursea_data.csv`
        alt = ROOT / "coursea_data.csv"
        if alt.exists():
            print("Found coursea_data.csv in repo root — using as programs source.")
            # try to pick reasonable columns
            df = pd.read_csv(alt)
            # try to standardize to name/description
            if "course_title" in df.columns:
                df_programs = df[[c for c in ["course_title", "course_difficulty"] if c in df.columns]]
                df_programs.columns = ["name", "difficulty"][: len(df_programs.columns)]
            else:
                df_programs = df.iloc[:, :2]
                df_programs.columns = ["name", "description"]
        else:
            print("No programs CSV found. Creating empty programs table.")
            df_programs = pd.DataFrame(columns=["name", "description"])
    else:
        df_programs = pd.read_csv(programs_csv)

    create_table_from_df(conn, "programs", df_programs)
    print(f"Created 'programs' table ({len(df_programs)} rows)")

    # 2) Students
    students_csv = BACKEND / "students.csv"
    if students_csv.exists():
        df_students = pd.read_csv(students_csv)
        create_table_from_df(conn, "students", df_students)
        print(f"Created 'students' table ({len(df_students)} rows)")
    else:
        print("No students CSV found; created empty 'students' table.")
        create_table_from_df(conn, "students", pd.DataFrame(columns=["student_id", "name", "primary_interest"]))

    # 3) Interactions -> map to `feedback` table
    interactions_csv = BACKEND / "interactions.csv"
    if interactions_csv.exists():
        df_inter = pd.read_csv(interactions_csv)
        create_table_from_df(conn, "feedback", df_inter)
        print(f"Created 'feedback' table ({len(df_inter)} rows)")
    else:
        print("No interactions CSV found; created empty 'feedback' table.")
        create_table_from_df(conn, "feedback", pd.DataFrame(columns=["student_id", "course_id", "rating", "interaction_type"]))

    # 4) recommendations table (empty)
    create_table_from_df(conn, "recommendations", pd.DataFrame(columns=["student_id", "program_id", "score"]))
    print("Created empty 'recommendations' table.")

    conn.close()
    print("✅ DB init complete.")


if __name__ == "__main__":
    main()
