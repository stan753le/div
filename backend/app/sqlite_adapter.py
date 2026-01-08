import sqlite3
import json
import uuid
from types import SimpleNamespace
from typing import Any


def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class Table:
    def __init__(self, conn: sqlite3.Connection, name: str):
        self.conn = conn
        self.name = name
        self._select = "*"
        self._where = []
        self._limit = None

    def select(self, cols: str = "*"):
        self._select = cols
        return self

    def eq(self, field: str, value: Any):
        self._where.append((field, "=", value))
        return self

    def in_(self, field: str, values):
        self._where.append((field, "IN", tuple(values)))
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def insert(self, data):
        cur = self.conn.cursor()
        if isinstance(data, list):
            if not data:
                return SimpleNamespace(data=[])

            # Add id if not present
            for item in data:
                if 'id' not in item:
                    item['id'] = str(uuid.uuid4())
                # Serialize JSON fields for students
                if self.name == 'students':
                    if 'interests' in item and isinstance(item['interests'], list):
                        item['interests'] = json.dumps(item['interests'])
                    if 'grades' in item and isinstance(item['grades'], dict):
                        item['grades'] = json.dumps(item['grades'])

            cols = list(data[0].keys())
            placeholders = ",".join(["?" for _ in cols])
            sql = f"INSERT INTO {self.name} ({', '.join(cols)}) VALUES ({placeholders})"
            values = [tuple(d.get(c) for c in cols) for d in data]
            cur.executemany(sql, values)
            self.conn.commit()
            return SimpleNamespace(data=data)
        elif isinstance(data, dict):
            # Add id if not present
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())

            # Serialize JSON fields for students
            if self.name == 'students':
                if 'interests' in data and isinstance(data['interests'], list):
                    data['interests'] = json.dumps(data['interests'])
                if 'grades' in data and isinstance(data['grades'], dict):
                    data['grades'] = json.dumps(data['grades'])

            cols = list(data.keys())
            placeholders = ",".join(["?" for _ in cols])
            sql = f"INSERT INTO {self.name} ({', '.join(cols)}) VALUES ({placeholders})"
            cur.execute(sql, tuple(data.get(c) for c in cols))
            self.conn.commit()

            # Return with parsed JSON for consistency
            result_data = dict(data)
            if self.name == 'students':
                if 'interests' in result_data and isinstance(result_data['interests'], str):
                    result_data['interests'] = json.loads(result_data['interests'])
                if 'grades' in result_data and isinstance(result_data['grades'], str):
                    result_data['grades'] = json.loads(result_data['grades'])

            return SimpleNamespace(data=[result_data])
        else:
            raise ValueError("Unsupported insert payload")

    def update(self, update_data: dict):
        cur = self.conn.cursor()
        if not self._where:
            raise ValueError("Unsafe update without WHERE")
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        params = list(update_data.values())
        where_clauses = []
        for f, op, val in self._where:
            if op == "IN":
                placeholders = ",".join(["?" for _ in val])
                where_clauses.append(f"{f} IN ({placeholders})")
                params.extend(list(val))
            else:
                where_clauses.append(f"{f} = ?")
                params.append(val)
        sql = f"UPDATE {self.name} SET {set_clause} WHERE {' AND '.join(where_clauses)}"
        cur.execute(sql, params)
        self.conn.commit()
        return SimpleNamespace(data=[{"updated": cur.rowcount}])

    def execute(self):
        cur = self.conn.cursor()
        cols = self._select
        sql = f"SELECT {cols} FROM {self.name}"
        params = []
        if self._where:
            clauses = []
            for f, op, val in self._where:
                if op == "IN":
                    placeholders = ",".join(["?" for _ in val])
                    clauses.append(f"{f} IN ({placeholders})")
                    params.extend(list(val))
                else:
                    clauses.append(f"{f} = ?")
                    params.append(val)
            sql += " WHERE " + " AND ".join(clauses)
        if self._limit:
            sql += f" LIMIT {self._limit}"
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

        # Parse JSON fields for specific tables
        if self.name == 'programs':
            for row in rows:
                if 'tags' in row and isinstance(row['tags'], str):
                    try:
                        row['tags'] = json.loads(row['tags'])
                    except:
                        row['tags'] = []
                if 'skills' in row and isinstance(row['skills'], str):
                    try:
                        row['skills'] = json.loads(row['skills'])
                    except:
                        row['skills'] = []
                if 'requirements' in row and isinstance(row['requirements'], str):
                    try:
                        row['requirements'] = json.loads(row['requirements'])
                    except:
                        row['requirements'] = {}

        if self.name == 'students':
            for row in rows:
                if 'interests' in row and isinstance(row['interests'], str):
                    try:
                        row['interests'] = json.loads(row['interests'])
                    except:
                        row['interests'] = []
                if 'grades' in row and isinstance(row['grades'], str):
                    try:
                        row['grades'] = json.loads(row['grades'])
                    except:
                        row['grades'] = {}

        # reset query state
        self._select = "*"
        self._where = []
        self._limit = None
        return SimpleNamespace(data=rows)


def create_client(db_path: str = "./backend/data.db"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = _dict_factory

    class Client:
        def __init__(self, conn):
            self.conn = conn

        def table(self, name: str):
            return Table(self.conn, name)

        def execute_sql(self, sql: str, params=()):
            cur = self.conn.cursor()
            cur.execute(sql, params)
            try:
                rows = [dict(r) for r in cur.fetchall()]
            except Exception:
                rows = []
            self.conn.commit()
            return SimpleNamespace(data=rows)

    return Client(conn)
