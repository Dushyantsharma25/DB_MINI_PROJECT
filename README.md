Student Project Management System (Flask + MySQL)
A mini project management web application built using Flask and MySQL. This system allows students, guides, and coordinators to manage academic projects, assign tasks, track progress, and collaborate efficiently.
Features
• User authentication (Register/Login/Logout)
• Role-based access — Student, Guide, and Coordinator
• Create, update, and delete projects
• Add team members and assign roles
• Add and manage project tasks with progress tracking
• Dynamic progress bar based on task completion
• Simple, clean UI with inline alerts and confirmation prompts
Tech Stack
Component	Technology
Backend	Flask (Python)
Database	MySQL
Frontend	HTML + CSS (inline templates)
Authentication	Werkzeug Security (hashed passwords)
Installation Guide
Follow these steps to set up and run this project on your local machine:
1.	1️⃣ Clone this repository:
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
2.	2️⃣ Set up a virtual environment (recommended):
python -m venv venv
source venv/Scripts/activate (Windows)
source venv/bin/activate (Linux/Mac)
3.	3️⃣ Install dependencies:
pip install flask mysql-connector-python werkzeug
4.	4️⃣ Configure MySQL Database:
CREATE DATABASE project_mgmt;
Then edit DB_CONFIG in app.py to match your MySQL username and password.
5.	5️⃣ Run the application:
python app.py
6.	6️⃣ Access in your browser:
http://127.0.0.1:5000
Default Roles & Functionalities
• Student: Create projects, add tasks, invite team members
• Guide: View assigned projects, update task statuses
• Coordinator: View all projects and statuses
Database Schema Overview
Tables created automatically on first run:
1. users — stores login details and roles
2. projects — stores project info and links to creator/guide
3. project_members — maintains team structure
4. tasks — manages project tasks and progress
Example Workflow
1. Register as a Student and login.
2. Create a new project and optionally assign a Guide.
3. Add Tasks and mark their progress.
4. Add Team Members by username.
5. Guides can view assigned projects and update tasks.
6. Coordinators can view all projects.
Author
Dushyant Krishna Sharma
📧 your-email@example.com
🌐 GitHub: https://github.com/<your-username>
