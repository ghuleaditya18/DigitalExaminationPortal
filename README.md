# Digital Examination Portal

## Project Description

Digital Examination Portal is a web-based application developed using Django that enables administrators to manage online examinations efficiently. 
The system allows user management, subject management, question management, online test conduction, result generation, and performance tracking through an interactive interface.

## Features

- User Registration and Login
- Role-Based Access Control
- Subject Management
- Question Management
- Online Examination System
- Automatic Result Calculation
- Score and Percentage Display
- Student Profile Management
- Password Reset Verification
- Feedback Management
- Responsive User Interface

## Technologies Used

- Python
- Django
- MySQL
- HTML5 / CSS3 / Bootstrap
- JavaScript
- Git / GitHub

## Installation & Setup Guide

### 1. Clone the repository

```bash
git clone https://github.com/ghuleaditya18/DigitalExaminationPortal.git
cd DigitalExaminationPortal
```

### 2. Create and activate a virtual environment

Windows:
```cmd
python -m venv env
env\Scripts\activate
```

Linux / macOS:
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to create your local `.env` file:

Windows:
```cmd
copy .env.example .env
```

Linux / macOS:
```bash
cp .env.example .env
```

Edit `.env` and fill in your secure local configuration:
- `SECRET_KEY`: Set a cryptographically secure Django secret key.
- `DEBUG`: Set to `True` for development, `False` for production.
- `DB_NAME`: MySQL database name (e.g., `OnlineTestPortal1311db`).
- `DB_USER`: MySQL database username.
- `DB_PASSWORD`: MySQL database password.
- `DB_HOST`: MySQL host (e.g., `localhost`).
- `DB_PORT`: MySQL port (default `3306`).
- `ALLOWED_HOSTS`: Comma-separated allowed hostnames.

### 5. Configure MySQL Database

Ensure MySQL is running and create the database:

```sql
CREATE DATABASE OnlineTestPortal1311db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Apply Migrations

```bash
python manage.py migrate
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
