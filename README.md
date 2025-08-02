# 🐾 Veterinary Assistant

> An AI-powered veterinary diagnostic system built for the VIRTUSA JatayuS4 TechMarshals hackathon

## 📋 Overview

The Veterinary Assistant is an intelligent application that leverages computer vision and machine learning to assist veterinarians in diagnosing animal health conditions. The system combines multiple AI models including YOLOv8 for object detection, image classification for disease prediction, and natural language processing for comprehensive veterinary reports.

## ✨ Key Features

- **🔍 AI-Powered Disease Detection**: Advanced image analysis using YOLOv8 models for detecting various animal health conditions
- **🤖 AI Assistant (RAG)**: Intelligent conversational assistant using LangChain and ChromaDB for context-aware veterinary guidance
- **📊 Interactive Dashboard**: Real-time monitoring and visualization using Grafana
- **📝 Automated Report Generation**: LLM-based report creation using LangGraph
- **☁️ Cloud Integration**: Google Drive integration for seamless data management
- **🌍 Location Mapping**: Geographic tracking and region-based analytics
- **📱 User-Friendly Interface**: PyQt5-based desktop application with intuitive design
- **🗄️ Robust Data Management**: SQLite database with comprehensive schema
- **🔒 Secure Authentication**: Encrypted credential management

## 🏗️ Project Architecture

### 📁 Directory Structure

#### `/assets/`
Static visual assets used in GUI and reports including:
- Animal disease reference images (anthrax, blackleg, lumpskin, mastitis, mouth conditions)
- UI fonts (DejaVuSans family in multiple weights)
- Application icons and visual elements

#### `/auth/`
Encrypted credentials and authentication components:
- `credentials.json.enc` - Encrypted API credentials
- `token.pickle.enc` - Encrypted authentication tokens
- `chroma_encrypted.bin` - Encrypted ChromaDB vector database for AI assistance
- `disease_prediction_model.pkl.enc` - Encrypted ML model for disease prediction

#### `/backend/yolomodels/`
Encrypted YOLOv8 detection models:
- `bcs.pt.enc` - Body Condition Scoring model
- `lumpy.pt.enc` - Lumpy Skin Disease detection model
- `mouth.pt.enc` - Oral/mouth health assessment model

#### `/huggingface/`
RAG (Retrieval-Augmented Generation) components:
- `config.json` - Model configuration settings
- `tokenizer.json` - Text tokenization configuration
- `vocab.json` - Vocabulary mappings
- `special_tokens_map.json` - Special token definitions

#### `/grafana/`
Offline Grafana server and visualization setup:
- `bin/grafana-server.exe` - Standalone Grafana server executable
- `conf/dashboards/virtusa_final.json` - Custom dashboard configuration
- `conf/datasource/sqlite_datasource.json` - Database connection settings
- `conf/plugins/` - Additional Grafana plugins
- `data/logs/` - Application and system logs

### 🐍 Core Python Modules

- **`app.py`** - Flask web server providing REST APIs for the dashboard and external integrations
- **`llmodel.py`** - LangGraph-powered report generation system with LangChain integration for intelligent veterinary reports and AI assistance
- **`drive.py`** - Google Drive integration module for cloud storage and file synchronization
- **`location.py`** - Geographic mapping and region-based analytics for disease tracking
- **`imagetest.py`** - Standalone testing script for AI model validation and performance testing
- **`model2.py`** - Secondary AI model integration for enhanced detection capabilities
- **`temptrack.py`** - Temperature monitoring and logging system (optional environmental tracking)
- **`sqlite.py`** - Database management system with custom schema for veterinary data
- **`setup.py`** - Application packaging and distribution script
- **`main.py`** - Primary PyQt5 desktop application interface and controller

### 🛠️ Additional Components

#### `/inno_setup/`
Windows installer builder:
- `VeterinaryAssistantInstaller.iss` - Inno Setup script for creating Windows installer
- `icon.ico` - Application icon for installer

## 🤖 AI Models & Capabilities

### Computer Vision Models
- **Body Condition Scoring (BCS)**: Automated assessment of animal body condition using visual analysis
- **Lumpy Skin Disease Detection**: Specialized model for identifying lumpy skin disease in livestock
- **Oral Health Assessment**: Mouth condition analysis for comprehensive health evaluation

### AI Assistance
- **Report Generation**: Automated veterinary report creation using LangGraph workflow orchestration
- **AI Assistant**: LangChain-powered conversational AI with ChromaDB vector storage for context-aware responses
- **Data Analysis**: Intelligent interpretation of diagnostic results and historical data patterns

### Data Processing & Detection
- **Image-Based Disease Detection**: Computer vision pipeline for analyzing animal images and identifying health conditions
- **Multi-Disease Classification**: Simultaneous detection of multiple conditions from single image inputs
- **Historical Trend Analysis**: Pattern recognition in animal health data over time

## 📊 System Components

### Database Management
- **SQLite Integration**: Lightweight, embedded database for storing diagnostic results
- **Data Schema**: Comprehensive structure for veterinary data including diagnostic results

### Visualization & Monitoring
- **Grafana Dashboards**: Real-time visualization of disease detection statistics and cattle health trends using data from SQLite database
- **Disease Distribution Charts**: Visual representation of detected diseases across different cattle populations
- **Alert Systems**: Automated notifications for critical health conditions or unusual disease patterns

### Security & Authentication
- **Encrypted Storage**: All sensitive data including models, credentials, and patient information is encrypted at rest
- **Secure API Access**: Token-based authentication for web services and cloud integrations

## 🌟 Team: TechMarshals

This project represents an innovative AI solution for veterinary healthcare, developed as part of the VIRTUSA JatayuS4 hackathon. The system demonstrates advanced integration of computer vision, natural language processing, and cloud technologies to create a comprehensive diagnostic platform for veterinary professionals.

---

**Built with cutting-edge AI technology for advancing animal healthcare** 🐾
