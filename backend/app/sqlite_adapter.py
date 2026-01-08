import sqlite3
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
            cols = list(data[0].keys())
            placeholders = ",".join(["?" for _ in cols])
            sql = f"INSERT INTO {self.name} ({', '.join(cols)}) VALUES ({placeholders})"
            values = [tuple(d.get(c) for c in cols) for d in data]
            cur.executemany(sql, values)
            self.conn.commit()
            return SimpleNamespace(data=data)
        elif isinstance(data, dict):
            cols = list(data.keys())
            placeholders = ",".join(["?" for _ in cols])
            sql = f"INSERT INTO {self.name} ({', '.join(cols)}) VALUES ({placeholders})"
            cur.execute(sql, tuple(data.get(c) for c in cols))
            self.conn.commit()
            return SimpleNamespace(data=[data])
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
