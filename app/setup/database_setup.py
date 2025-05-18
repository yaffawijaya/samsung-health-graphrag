# database_setup.py

import toml
from sqlalchemy import create_engine, text

# Load credentials from secrets.toml
cfg = toml.load('secrets.toml')['mysql']
url = (
    f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
    f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
)
engine = create_engine(url)

# Revised schema: include chat_sessions and chat_history
schema_sql = """
-- Users table with surrogate primary key
CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Food intake
CREATE TABLE IF NOT EXISTS food_intake (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  event_time DATETIME,
  food_name VARCHAR(255),
  amount FLOAT,
  calories FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Water intake
CREATE TABLE IF NOT EXISTS water_intake (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  event_time DATETIME,
  amount FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sleep hours
CREATE TABLE IF NOT EXISTS sleep_hours (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  date DATE,
  total_sleep_h FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Step count
CREATE TABLE IF NOT EXISTS step_count (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  date DATE,
  total_steps INT,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Existing health tables omitted for brevity...

-- Chat sessions: one per conversation thread
CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(255) NOT NULL DEFAULT 'New chat',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_user_created_at (user_id, created_at)
) ENGINE=InnoDB;

-- Chat history: messages per session
CREATE TABLE IF NOT EXISTS chat_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT NOT NULL,
  role ENUM('user','assistant') NOT NULL,
  message TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
  INDEX idx_session_created_at (session_id, created_at)
) ENGINE=InnoDB;
"""

# Execute the schema creation queries
with engine.begin() as conn:
    try:
        for statement in schema_sql.strip().split(';'):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        print("All tables (including chat sessions and history) created or already exist.")
    except Exception as e:
        print(f"An error occurred during schema creation: {e}")
