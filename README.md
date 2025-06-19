# 🧠 AI Project Monitor

**AI Project Monitor** is a role-based project and task management web application built with **Django**. It enables efficient collaboration between managers and developers while offering **AI-powered insights** for admins using **LangChain**, **LLaMA 3.1**, and **CrewAI**.

---

## 📌 Table of Contents

- [🚀 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🧑‍💼 User Roles](#-user-roles)
- [🎯 Project Objectives](#-project-objectives)
- [📊 AI-Powered Insights](#-ai-powered-insights)
- [📄 License](#-license)

---

## 🚀 Features

### 🔐 1. Role-Based Access Control

- **Admin (Superuser)**: Manages roles and accesses AI insights.
- **Manager**: Creates projects, assigns tasks, and monitors progress.
- **Developer**: Views and updates tasks assigned to them.

### 📁 2. Project & Task Management

- Managers can perform CRUD operations on projects.
- Tasks can be assigned to developers with due dates.
- Developers can update the status of their assigned tasks.

### 💬 3. Real-Time Commenting System

- Threaded comments between managers and developers for each task.
- Ensures ongoing feedback and clarity on task progress.

### 📧 4. Email Notifications

- Developers receive notifications when tasks are assigned or updated.
- Managers are notified when developers update a task.

### 🤖 5. AI-Driven Summaries (Admin Only)

- Generate project summaries and improvement suggestions using **LLaMA 3.1 8B** (via Groq + LangChain).
- Insights are derived from projects, tasks, and task-level discussions.

### 🧩 6. CrewAI-Based Agent System (Admin Only)

Multi-agent architecture powered by **CrewAI**:

- **Project Health Analyst**: Evaluates project status and delays.
- **Workload Analyst**: Assesses developer workload and suggests reassignments.
- **Report Synthesizer**: Consolidates insights into a structured, actionable report.

---

## 🛠️ Tech Stack

| Category             | Tools/Technologies                                 |
|----------------------|----------------------------------------------------|
| Backend Framework    | Django (Python)                                    |
| Frontend             | HTML, CSS, Bootstrap (Django Templates)            |
| Database             | SQLite (Development)                               |
| Authentication       | Django User Model + Groups                         |
| AI Integration       | LangChain + Groq (LLaMA 3.1 8B Instant)             |
| Multi-Agent System   | CrewAI                                              |

---

## 🧑‍💼 User Roles

- **Admin**:
  - Assigns roles (Manager/Developer)
  - Generates AI summaries and reports

- **Manager**:
  - Creates and manages projects/tasks
  - Communicates with developers

- **Developer**:
  - Views and updates assigned tasks
  - Collaborates through the comment system

---

## 🎯 Project Objectives

- Provide a structured platform for managing projects and tasks.
- Enforce clear role-based access and permissions.
- Support seamless communication between team members.
- Offer AI-powered insights for better project decisions.
- Enable detailed project monitoring using intelligent agents.

---

## 📊 AI-Powered Insights

> 🧠 Admin-exclusive features for smarter project management:

- Project summaries and actionable improvement suggestions
- Detection of stalled tasks and progress blockers
- Developer workload analysis and balance
- Suggested task reassignments
- Structured reports from CrewAI agents

**LLM Used**: `LLaMA-3.1-8B-Instant` via **Groq** with **LangChain** integration

---

## 🚀 Powered By These Technologies

<p align="left">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge" />
  <img src="https://img.shields.io/badge/CrewAI-purple?style=for-the-badge" />
</p>


---

## 📄 License

This project was developed as part of my internship and has been submitted as the final project for the same.  
It is intended for academic and evaluation purposes only. Licensing terms can be defined if the project is extended or reused in the future.


