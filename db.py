import sqlite3

DB_PATH = "babybot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        line_user_id TEXT PRIMARY KEY,
        stage TEXT,              -- 'pregnant' or 'born'
        due_date TEXT,           -- YYYY-MM-DD
        birth_date TEXT,         -- YYYY-MM-DD
        baby_gender TEXT,        -- 'M' or 'F'
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_state (
        line_user_id TEXT PRIMARY KEY,
        step TEXT,               -- 'ask_stage','ask_due','ask_birth','ask_gender','done'
        temp_stage TEXT,
        temp_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def set_state(line_user_id, step, temp_stage=None, temp_date=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO user_state(line_user_id, step, temp_stage, temp_date)
    VALUES(?,?,?,?)
    ON CONFLICT(line_user_id) DO UPDATE SET
        step=excluded.step,
        temp_stage=excluded.temp_stage,
        temp_date=excluded.temp_date
    """, (line_user_id, step, temp_stage, temp_date))
    conn.commit()
    conn.close()

def get_state(line_user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT step, temp_stage, temp_date FROM user_state WHERE line_user_id=?", (line_user_id,))
    row = cur.fetchone()
    conn.close()
    return row  # (step, temp_stage, temp_date) or None

def save_user(line_user_id, stage, date_str, gender):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    due_date = date_str if stage == "pregnant" else None
    birth_date = date_str if stage == "born" else None
    cur.execute("""
    INSERT INTO users(line_user_id, stage, due_date, birth_date, baby_gender)
    VALUES(?,?,?,?,?)
    ON CONFLICT(line_user_id) DO UPDATE SET
        stage=excluded.stage,
        due_date=excluded.due_date,
        birth_date=excluded.birth_date,
        baby_gender=excluded.baby_gender
    """, (line_user_id, stage, due_date, birth_date, gender))
    # 完成後把狀態設 done
    set_state(line_user_id, "done")
    conn.commit()
    conn.close()

    import sqlite3

DB_PATH = "babybot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        line_user_id TEXT PRIMARY KEY,
        stage TEXT,              -- 'pregnant' or 'born'
        due_date TEXT,           -- YYYY-MM-DD
        birth_date TEXT,         -- YYYY-MM-DD
        baby_gender TEXT,        -- 'M' or 'F'
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_state (
        line_user_id TEXT PRIMARY KEY,
        step TEXT,               -- 'ask_stage','ask_due','ask_birth','ask_gender','done'
        temp_stage TEXT,
        temp_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def set_state(line_user_id, step, temp_stage=None, temp_date=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO user_state(line_user_id, step, temp_stage, temp_date)
    VALUES(?,?,?,?)
    ON CONFLICT(line_user_id) DO UPDATE SET
        step=excluded.step,
        temp_stage=excluded.temp_stage,
        temp_date=excluded.temp_date
    """, (line_user_id, step, temp_stage, temp_date))
    conn.commit()
    conn.close()

def get_state(line_user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT step, temp_stage, temp_date FROM user_state WHERE line_user_id=?", (line_user_id,))
    row = cur.fetchone()
    conn.close()
    return row  # (step, temp_stage, temp_date) or None

def get_user(line_user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT stage, due_date, birth_date
    FROM users
    WHERE line_user_id=?
    """, (line_user_id,))
    row = cur.fetchone()
    conn.close()
    return row  # (stage, due_date, birth_date) or None

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT line_user_id, stage, due_date, birth_date
    FROM users
    """)
    rows = cur.fetchall()
    conn.close()
    return rows