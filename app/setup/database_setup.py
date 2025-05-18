# database_setup.py
import toml
from sqlalchemy import create_engine, text

# Load credentials from secrets.toml
cfg = toml.load('secrets.toml')['mysql']
url = (
    f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
)
engine = create_engine(url)

# Revised schema: use user_id as PK and username as attribute
schema_sql = """
-- Users table with surrogate primary key
CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Food intake references user_id
CREATE TABLE IF NOT EXISTS food_intake (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  event_time DATETIME,
  food_name VARCHAR(255),
  amount FLOAT,
  calories FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Water intake references user_id
CREATE TABLE IF NOT EXISTS water_intake (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  event_time DATETIME,
  amount FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Sleep hours references user_id
CREATE TABLE IF NOT EXISTS sleep_hours (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  date DATE,
  total_sleep_h FLOAT,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Step count references user_id
CREATE TABLE IF NOT EXISTS step_count (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  date DATE,
  total_steps INT,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
"""

# Execute the schema creation queries
with engine.begin() as conn:
    try:
        for statement in schema_sql.strip().split(';'):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        print("All tables created or already exist with user_id as primary key.")
    except Exception as e:
        print(f"An error occurred during schema creation: {e}")
