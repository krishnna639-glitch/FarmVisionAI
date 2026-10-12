# 🌾 FarmVision AI - Crop Disease Detection & Management System

**FarmVision AI** is an intelligent web application designed to empower farmers and agricultural experts with instant, AI-driven crop disease diagnosis. By leveraging deep learning models, the system analyzes leaf images to detect diseases in real-time, offering actionable treatment advice to protect crop yields and promote sustainable farming practices.

---

## 🚀 Key Features

### 👤 User Features
* **AI Disease Scan:** Upload images of infected crop leaves for real-time diagnosis and confidence scoring.
* **Plant Disease Advisor:** Ask for symptoms, treatment, and prevention guidance for the supported potato and tomato conditions.
* **Interactive Dashboard:** View personal prediction history, diagnostic logs, and treatment recommendations.
* **Smart Farming Tips:** Access best practices for irrigation, crop rotation, and soil management.
* **Contact & Support Form:** Directly reach out to system administrators for assistance or feedback.

### 🛡️ Admin Features
* **Role-Based Access Control:** Secure authentication restricting management features to administrators.
* **User Management:** View, search, and manage registered user accounts.
* **Prediction Log Management:** Monitor, filter, and delete past prediction records across all users.
* **Contact Center:** Review, filter, and reply to user support inquiries.
* **Report Generation & Data Export:** One-click CSV exports for users, prediction logs, and contact messages, complete with a printable summary view.

---

## 🛠️ Tech Stack

| Layer | Technology / Library |
| :--- | :--- |
| **Backend Framework** | Python 3.x, Flask |
| **Database & ORM** | SQLite / PostgreSQL, Flask-SQLAlchemy |
| **Authentication** | Flask-Login, Werkzeug Security |
| **Frontend UI** | HTML5, Tailwind CSS, JavaScript (Vanilla ES6) |
| **AI / Machine Learning** | TensorFlow / PyTorch / OpenCV (Deep Learning CNN) |
| **Template Engine** | Jinja2 |

---

## 📁 Project Architecture

```text
farmvision-ai/
│
├── admin/                  # Admin Blueprint (Routes & Logic)
│   ├── __init__.py
│   └── routes.py           # User, Prediction, Contact & Report Routes
│
├── auth/                   # Authentication Blueprint
│   ├── __init__.py
│   └── routes.py           # Login, Register, Logout
│
├── models/                 # Database Schema Models
│   ├── user.py             # User Model (Roles: admin, user)
│   ├── prediction.py       # Crop Scan & Prediction Results Model
│   └── contact.py          # User Contact & Feedback Model
│
├── static/                 # Static Assets (Images, CSS, JS)
│   └── uploads/            # Stored user leaf scan images
│
├── templates/              # Jinja2 HTML Templates
│   ├── admin/              # Admin pages (dashboard, users, predictions, contacts, reports)
│   ├── base.html           # Main Layout Template
│   ├── home.html           # Interactive Landing Page
│   └── predict.html        # AI Scanner Interface
│
├── app.py                  # Main Application Entry Point
├── extensions.py           # DB & Login Manager Instances
└── requirements.txt        # Python Dependencies

```

---

## 🗄️ Database Schema Overview
```markdown
+-------------------+       +-----------------------+       +------------------------+
|       User        |       |      Prediction       |       |     ContactMessage     |
+-------------------+       +-----------------------+       +------------------------+
| id (PK, Integer)  | <---> | id (PK, Integer)      |       | id (PK, Integer)       |
| name (String)     | 1   N | user_id (FK, Integer) |       | name (String)          |
| email (String)    |       | filename (String)     |       | email (String)         |
| password (String) |       | result (String)       |       | message (Text)         |
| role (String)     |       | confidence (Float)    |       | created_at (DateTime)  |
+-------------------+       | created_at (DateTime) |       +------------------------+
                            +-----------------------+

```

⚡ Getting Started
1. Clone the Repository
Bash
git clone [https://github.com/your-username/FarmVisionAI.git](https://github.com/your-username/farmvision-ai.git)
cd farmvision-ai
2. Create & Activate Virtual Environment
Bash

### Windows
python -m venv venv
venv\Scripts\activate

### macOS / Linux
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
Bash
pip install -r requirements.txt
4. Run the Application
Bash
python app.py
Open your browser and navigate to http://127.0.0.1:5000.


---

## 🗄️ 1. Create `schema.sql`

Create a file named `schema.sql` in your project's root folder and paste the following SQL definitions:

```sql
-- Database Schema for FarmVision AI (SQLite / PostgreSQL / MySQL compatible)

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    result VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. Create Contact Messages Table
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Insert Default Admin User (Password: admin123 hashed via Werkzeug)
INSERT OR IGNORE INTO users (id, name, username, email, password, role) 
VALUES (
    1, 
    'System Administrator', 
    'admin', 
    'admin@farmvision.com', 
    'scrypt:32768:8:1$uQJ8...$hash_value_here', 
    'admin'
);

```

---

## 🛠️ 2. How Users Can Run the SQL File

There are **two easy ways** for anyone who clones project to execute this SQL script:

### Option A: Using SQLite Command Line (Simplest)

In the terminal, you can run a single command to create the database from `schema.sql`:

```bash
# Creates farmvision.db and executes all CREATE TABLE commands
sqlite3 instance/farmvision.db < schema.sql

```

---

### Option B: Automatic Execution via Python (`init_db.py`)

You can provide a small helper Python script that reads and runs `schema.sql` automatically using Python’s built-in `sqlite3` library:

Create `init_db.py`:

```python
import sqlite3
import os

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

# Connect to database and execute SQL script
conn = sqlite3.connect('instance/farmvision.db')
with open('schema.sql', 'r') as f:
    conn.executescript(f.read())

conn.close()
print("✅ Database tables successfully created from schema.sql!")

```

Running it is as simple as:

```bash
python init_db.py

```

---

## 📄 Update Your `README.md`

Add this section to your project's `README.md` under setup instructions:

```markdown
### 🗄️ Database Setup (SQL Script Method)

To initialize the database using the provided SQL schema:

```bash
# Option 1: Via Python runner script
python init_db.py

# Option 2: Directly via SQLite CLI
sqlite3 instance/farmvision.db < schema.sql

```

```

---

### 💡 Comparison: SQLAlchemy vs. SQL Script

| Method | Pros | Best For |
| :--- | :--- | :--- |
| **`db.create_all()` (SQLAlchemy)** | Zero manual steps; completely automated inside Flask on app startup. | Beginners or quick local development. |
| **`schema.sql` (Raw SQL)** | Explicit, transparent, easy to run in database tools (pgAdmin, DBeaver, SQLite Studio). | Production deployment, team collaboration, and grading/reviews. |

```
