<p align="center">
  <img src="static/images/Analytica_Logo.png" alt="Analytica Hub Logo" width="200"/>
</p>

# Analytica Hub

**AI-Powered Data Analysis Platform with Flask Microservices**

**Analytica Hub** is a scalable, AI-powered data analytics platform built with **Django**, **Flask**, **Redis**, **Celery**, and **Docker**. It enables users to upload large CSV files (up to lakhs of rows), perform Exploratory Data Analysis (EDA), and clean data automatically using a single-click AI-based process. The platform features a “**Chat with CSV**” interface powered by natural language, capable of returning both text-based and visual insights.

AI functionalities like EDA, data cleaning, and natural language querying are handled through a **Flask microservice** that communicates with the Django app via internal REST APIs. Redis ensures **real-time consistency** and avoids frequent database queries by maintaining intermediate states in memory.

---

## 🚀 Features

- 📂 Upload and process large CSV files (lakhs of rows supported)
- 📊 AI-powered **Exploratory Data Analysis (EDA)**
- 🧹 One-click **AI-based Data Cleaning**
- 💬 “**Chat with CSV**” using natural language queries
  - Supports **textual** and **graph-based** responses (max 5 graphs/chat)
- 🔄 Real-time undo/redo functionality using Redis
- 🧠 Flask microservice for scalable and isolated AI processing
- 🐳 Fully containerized using Docker
- 🏗️ Efficient server-to-server communication for microservices
- ⚡ Redis-powered in-memory consistency with reduced DB hits

---

## 🏗️ Architecture Overview

- **Django (Core App)** handles user management, CSV upload, task orchestration, and frontend (if any).
- **Flask Microservice** handles AI-heavy tasks: EDA, data cleaning, and natural language query processing.
- **Redis** maintains state after every operation, allowing low-level consistency and real-time undo/redo.
- **Celery** runs background tasks like calling the Flask microservice and storing processed CSVs.
- **Docker** ensures portability and isolation of services via separate containers for Django, Flask, Redis, and Celery workers.

---

## ⚙️ Tech Stack

- **Core Backend**: Django (no DRF)
- **AI Microservice**: Flask
- **Task Queue**: Celery
- **In-Memory Store**: Redis
- **Containerization**: Docker, Docker Compose
- **AI & Data Tools**: Pandas, Numpy, Matplotlib, Scikit-learn, Custom NLP
- **Communication**: Internal REST API (server-to-server)

---

## 🐳 Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/analytica-hub.git
cd analytica-hub
