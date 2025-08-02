
# 🐾 Veterinary Assistant

> An AI-powered livestock disease detection and health monitoring system built for the **VIRTUSA JatayuS4 TechMarshals Hackathon**

## 📋 Overview

**Veterinary Assistant** is a comprehensive AI-based diagnostic platform designed to assist veterinarians and farm owners in early identification of cattle diseases. Leveraging **computer vision**, **language models**, and **geospatial intelligence**, the system operates both **offline and online**, making it ideal for rural areas with limited internet access.

The platform integrates:
- **YOLOv8 models** for real-time disease detection  
- **LangGraph + Mistral (via LangChain)** for veterinary report generation and for Rag
- **ChromaDB RAG** for AI assistance  
- **Grafana dashboards** for health monitoring and analytics  
- **PyQt5 GUI** for user-friendly offline desktop control  

## ✨ Key Features

- **🔍 AI-Powered Disease Detection**: Detects multiple cattle diseases using YOLOv8 with real-time camera input  
- **🤖 Conversational AI Assistant (RAG)**: Built using LangChain + ChromaDB for veterinary queries  
- **🖥️ Offline & Online Deployment**: Works fully offline for field usage; integrates cloud sync based on the user selected Modes  
- **📊 Grafana Monitoring Dashboard**: Real-time data visualization with local SQLite backend  
- **📝 Report Generation**: LangGraph-powered intelligent report summaries (Mistral 7B) and Visualization 
- **☁️ Google Drive Sync**: Auto-upload Disease Detected Images to authenticated Drive folder for future model training  
- **🌍 Location Mapping**: Get nearby vet clininc Details 
- **🧠 Multi-Camera Input**: Supports 5–6 simultaneous camera streams from walking lanes  
- **🔐 Secure & Encrypted**: Credentials and models encrypted using Python Fernet  

## 🏗️ Project Architecture

### 📁 Directory Structure (Key Folders)

#### `/asset/`
Static visual elements used for display and report generation:
- Disease reference images (e.g., anthrax, blackleg, FMD)
- Fonts (DejaVuSans family)
- Visual design assets/icons

#### `/auth/`
All sensitive, encrypted files:
- `credentials.json.enc` — OAuth credentials
- `token.pickle.enc` — Auth token for Google Drive
- `chroma_encrypted.bin` — Chroma vector store
- `index.enc` — Embedding index
- `disease_prediction_model.pkl.enc` — ML classification model

#### `/backend/yolomodels/`
Encrypted YOLOv8 detection models:
- `bcs.pt.enc` — Body Condition Score
- `lumpy.pt.enc` — Lumpy Skin Disease
- `mouth.pt.enc` — Oral/mouth/FMD detection

#### `/huggingface/`
Embedding + tokenizer files for RAG:
- `config.json`, `tokenizer.json`, `vocab.json`, `special_tokens_map.json`

#### `/grafana/`
Offline-ready Grafana dashboard:
- `bin/` — Grafana server executable
- `conf/` — Contains dashboard JSON, SQLite datasource, plugins
- `data/` and `logs/` — Auto-generated at runtime

#### `/inno_setup/`
Installer packaging files:
- `VeterinaryAssistantInstaller.iss` — Inno Setup script
- `icon.ico` — App icon

## 🐍 Core Python Modules

| Module        | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `main.py`     | **Main GUI launcher** (PyQt5 + camera feed + real-time detection)           |
| `app.py`      | Flask backend for web dashboard, Grafana bridge, and LLM API                |
| `llmodel.py`  | LLM pipeline using LangChain + Mistral                                      |
| `drive.py`    | Google Drive integration and sync                                           |
| `location.py` | To get the nearby vet clininc details                                       |
| `model2.py`   | YOLOv8 model runner and detection helper (used by GUI)                      |
| `imagetest.py`| Script to test models on local images                                       |
| `temptrack.py`| Track and store the decryption model directory for deletion                 |
| `sqlite.py`   | Lightweight database manager using SQLite                                   |
| `setup.py`    | cx_Freeze/Nuitka build script for packaging                                 |
| `reportgen.py`| Report generation using Langgraph                                           |

## 🧠 AI Models & Capabilities

### Computer Vision (YOLOv8)
- **BCS (Body Condition Scoring)**: Visual estimation of cattle condition
- **Lumpy Skin Disease**: Accurate lesion detection and pattern match
- **Oral Disease/FMD**: Lesion detection in the mouth and muzzle

### AI Assistance (NLP + LangGraph)
- **Report Generation**: Summary reports of detections and health risks
- **RAG Assistant**: Domain-specific conversational support using LangChain + Chroma
- **Multi-Camera Support**: Simultaneous processing of 5–6 video feeds from farm walking lanes

### Offline Support
- Entire solution (GUI, inference, logging, dashboard) works **without internet**
- All logs and reports are locally stored and synced when online

## 📊 System Components

### 🗃️ Database
- **SQLite**: Offline-native database for storing all detections
- **Used in**: Grafana panels, local logs, historical tracking

### 📈 Visualization
- **Grafana**: Live dashboard showing disease spread and detection count
- **Dashboards**: Bar, stat, table, and gauge panels for different models
- **SQLite plugin**: Enables Grafana to read from local `.db` file

### 🔐 Security
- **Fernet encryption** used to secure:
  - Google credentials
  - AI model files, Frontend file
  - Vector store and indexes

## 💻 Technologies Used

### 🧠 Computer Vision & Machine Learning
- **YOLOv8** – Real-time object detection (Ultralytics)
- **OpenCV** – Image preprocessing and camera integration
- **Random Forest Classifier** – Backup ML model for classification
- **NumPy**, **Pillow** – Array/image processing tools

### 🤖 RAG & Language Models
- **Mistral 7B** – LLM for veterinary report generation (via Hugging Face)
- **LangChain** – Prompt flows and LLM orchestration
- **LangGraph** – Report generation
- **Chroma / ChromaDB** – Vector database for AI assistant
- **HuggingFace Transformers** – Tokenizer and embedding tools
- **Deep Translator** – Optional translation support

### 🖥️ User Interface
- **PyQt5** – Desktop GUI for local/offline mode
- **HTML / CSS / JS** – Used in Grafana dashboards and Flask routes

### 🛠️ Backend & APIs
- **Flask** – Web backend and REST API services
- **SQLite** – Lightweight, embedded database
- **cryptography.fernet** – Secure encryption of sensitive files
- **RapidAPI** – For external APIs (Vet Clinic Location)
- **OpenStreetMap** – Regional visualization and mapping

### 📦 Packaging & Deployment
- **cx_Freeze** – EXE builder for Python apps
- **Inno Setup** – Final installer builder for Windows

## 👥 Team: TechMarshals

Developed for the **Virtusa JatayuS4 Hackathon**, this project addresses a real-world problem with modern AI, making veterinary care accessible and scalable — even in the most remote regions of India.

---

**Built to protect our cattle farms, and empower veterinary science through AI** 🐮🚀
