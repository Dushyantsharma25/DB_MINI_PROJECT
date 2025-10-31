# 🧾 Student Project Management System

## 📘 Overview
The **Student Project Management System** is a C++-based console application designed to efficiently manage student academic projects.  
It allows users to **add**, **search**, **update**, **delete**, and **display** project details such as project title, team members, guide, and project status.  
This system uses **file handling** for data storage, ensuring persistence and easy retrieval.

---

## 🛠️ Features
- ➕ **Add New Project:** Enter and store project details.
- 🔍 **Search Project:** Find a specific project by title.
- 📋 **View All Projects:** Display all projects in a structured format.
- ✏️ **Update Project:** Modify existing project details.
- ❌ **Delete Project:** Remove a project from the record.
- 💾 **File-Based Storage:** Data stored in a simple text file (`data.txt`).

---

## 🧩 System Structure
StudentProjectManagement/
├── main.cpp
├── project.h
├── project.cpp
└── data.txt
---

## 💻 Technologies Used
- **Language:** C++  
- **Compiler:** GCC / G++  
- **IDE:** Visual Studio Code / Code::Blocks / Dev C++  
- **Operating Systems:** Windows / Linux / macOS  

---

## ⚙️ Compilation and Execution

### 🧱 Compile:
```bash
g++ main.cpp project.cpp -o project_manager
Run:
bash
Copy code
./project_manager
(Use project_manager.exe on Windows)

🧑‍💻 Menu Example
markdown
Copy code
========================================
     STUDENT PROJECT MANAGEMENT SYSTEM
========================================
1. Add New Project
2. View All Projects
3. Search Project
4. Update Project
5. Delete Project
6. Exit
Enter your choice:
📂 Sample Output
yaml
Copy code
Project Title: AI-Based Traffic System
Team Members: Dushyant, Riya, Arjun
Guide: Prof. Mehta
Status: Ongoing
----------------------------------------
Project Title: Spam Email Detection
Team Members: Balaji, Rohan
Guide: Dr. Sharma
Status: Completed
----------------------------------------
🚀 Future Enhancements
🗄️ Integrate database support (MySQL/SQLite).

🔐 Add login authentication for admin and students.

🖥️ Develop a GUI using Qt or Python Tkinter.

📊 Include project evaluation and grading module.

🧾 Export project data to PDF or Excel.

