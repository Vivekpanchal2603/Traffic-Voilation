# 🚦 Traffic AI Violation Detection System

An AI-powered traffic surveillance system for automated detection of traffic violations using computer vision and multimodal large language models.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?style=flat&logo=fastapi)
![YOLOv8](https://img.shields.io/badge/YOLOv8-8.0+-orange?style=flat&logo=pytorch)
![Ollama](https://img.shields.io/badge/Ollama-0.1+-purple)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Output Format](#-output-format)
- [License](#-license)

---

## ✨ Features

### 🔍 Helmet Detection
- Uses custom YOLO model (`best.pt`) trained to detect riders without helmets
- Processes video frames to identify no-helmet violations
- Saves violation frames for review

### 🛑 Triple Seat Detection
- Leverages local multimodal LLM (Ollama MiniCPM-V)
- Analyzes cropped bike/rider images to detect triple riding violations
- Intelligent image selection for accurate detection

### 🔢 Number Plate Recognition
- Extracts Indian vehicle number plates from detected plate crops
- Uses Ollama vision model for OCR
- Validates and cleans plate text for accuracy

### 🎨 Smart UI
- Interactive dashboard with modern glassmorphism design
- Video upload with preview
- Detection result cards with violation details
- Plate crop preview
- Click-to-enlarge images for detailed inspection

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | FastAPI, Uvicorn |
| **AI/ML** | YOLOv8, Ultralytics, Ollama (MiniCPM-V) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Video Processing** | OpenCV (cv2) |
| **Python** | 3.10+ |

---

## 📂 Project Structure

```
major_project/
│
├── README.md                    # This file
├── requirements.txt             # Project dependencies
│
├── backend/
│   ├── requirements.txt         # Backend dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── upload.py    # Video upload endpoint
│   │   │       ├── process.py   # Video processing endpoint
│   │   │       └── results.py   # Results retrieval endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py        # Configuration settings
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py      # Video processing orchestration
│   │   │   ├── plate_reader.py  # Number plate recognition
│   │   │   ├── storage.py        # File storage utilities
│   │   │   └── yolo_engine.py   # YOLO detection logic
│   │   └── static/
│   │       ├── index.html       # Frontend UI
│   │       ├── script.js        # Frontend JavaScript
│   │       └── style.css        # Frontend styles
│   │
│   └── models/
│       ├── best.pt              # Custom YOLO model (helmet detection)
│       └── yolov8n.pt           # YOLOv8 nano model
│
├── outputs/                     # Detection results storage
│   └── {job_id}/
│       ├── full_frames/         # Violation frame images
│       ├── plates/              # Cropped plate images
│       └── triple_crop/         # Triple riding crop images
│
└── uploads/                     # Uploaded video files
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
cd major_project
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai), then pull the vision model:

```bash
ollama pull minicpm-v
```

### 5. Download YOLO Models

Place your trained YOLO model as `backend/models/best.pt`. A pre-trained YOLOv8 model (`yolov8n.pt`) is also included for reference.

---

## 🚀 Usage

### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 2. Open the Web Interface

Navigate to `http://localhost:8000` in your web browser.

### 3. Upload and Process Video

1. Click on the upload area or drag & drop a video file
2. Preview the video in the player
3. Click "Upload & Analyze" to process
4. View detection results with violation details

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload video file |
| `POST` | `/api/process/{job_id}` | Process uploaded video |
| `GET` | `/api/results/{job_id}` | Get detection results |

### API Usage Example

```bash
# Upload video
curl -X POST -F "file=@video.mp4" http://localhost:8000/api/upload

# Process video
curl -X POST http://localhost:8000/api/process/{job_id}

# Get results
curl http://localhost:8000/api/results/{job_id}
```

---

## ⚙️ Configuration

Key configuration options in `backend/app/services/plate_reader.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `OLLAMA_MODEL` | `minicpm-v` | Ollama vision model |
| `MAX_PLATE_IMAGES` | `2` | Max plate images to process |
| `MAX_TRIPLE_IMAGES` | `1` | Max triple riding images |

YOLO configuration in `backend/app/services/yolo_engine.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CONF_THRESH` | `0.30` | YOLO confidence threshold |
| `TOP_PLATE_COUNT` | `25` | Top plates to save |
| `TOP_FULL_COUNT` | `10` | Top full frames to save |

---

## 📤 Output Format

Detection results are stored in `outputs/{job_id}/`:

```json
{
  "job_id": "uuid",
  "violations": {
    "no_helmet": true,
    "triple_riding": true,
    "plate_number": "MH01AB1234"
  },
  "files": {
    "plates": ["plate_best_0.jpg", "plate_best_1.jpg"],
    "full_frames": ["frame_0.jpg", "frame_1.jpg"],
    "triple_crops": ["triple_0.jpg"]
  }
}
```

---

## 📄 License

This project is for educational and research purposes. Ensure compliance with local laws and regulations when using AI surveillance systems.

---

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com) - YOLOv8
- [Ollama](https://ollama.com) - Local LLM infrastructure
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework