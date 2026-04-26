# SOFTWARE-PROJECT
CashFlow: A Modular Personal Finance & Budget Management System  A robust Django web application designed for real-time tracking of incomes, expenses, and recurring bills. Built with a focus on modular architecture (MTV) and integrated with a cloud-hosted MySQL database (Aiven) for collaborative financial management.


## 🛠 Prerequisites
Ensure you have the following installed on your local machine:
* Python 3.10+
* Git
* A terminal (PowerShell, Bash, or CMD)

---

## 🚀 Setup Instructions for Groupmates

To get this running on your machine, follow these steps exactly:

### 1. Clone and Enter the Project
```bash
git clone <your-repository-url>
cd SOFTWARE-PROJECT
```

### 2. Set Up the Virtual Environment
```bash
python -m venv venv
# Activate it:
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secret Environment Variables
Since the `.env` file is hidden for security, you must create your own:
1. Create a new file named `.env` in the root folder.
2. Ask **Javed** for the database credentials and paste them in:
   ```text
   DB_NAME=defaultdb
   DB_USER=avnadmin
   DB_PASSWORD=xxxxxxx
   DB_HOST=xxxxxxx.aivencloud.com
   DB_PORT=xxxxx
   SECRET_KEY=xxxxxxx
   DEBUG=True
   ```
3. Place the `ca.pem` certificate (provided by Javed) in the root folder.

### 5. Run the Server
You don't need to run `migrate` unless the database structure has changed.
```bash
python manage.py runserver
```

---

## 📂 Project Structure
* `/cashflow/` - Core project settings and configuration.
* `/users/` - User authentication and profiles.
* `/transactions/` - Income and expense tracking logic.
* `/analytics/` - Data visualization and reports.

## 🤝 Contribution Rules
* **Always** activate your `venv` before working.
* If you install a new package, run `pip freeze > requirements.txt` before committing.
* **Never** delete the `.env` file or upload it to GitHub.

### Why this README is "Pro-Level":
1. **Scannability:** It uses code blocks so your friends can just "Copy-Paste" commands.
2. **Clear Warnings:** It explicitly tells them they need the `.env` and `ca.pem` from you, which prevents them from messaging you at 2 AM asking why the code isn't working.
3. **Professionalism:** It shows your professor that you understand **Environment Isolation** (using `venv`) and **Secure Configuration** (using `.env`).

**Do you want to add a section on how to use Git branches for the different modules (Users, Transactions, Analytics)?**
