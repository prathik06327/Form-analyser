**Form Analyser**

**Description:** This repository contains a backend computer-vision service and supporting code to analyze human movement and provide assessment and feedback. The backend uses a pose model (yolo11n-pose.pt) and a collection of biomechanics, scoring, repetition detection, and feedback modules to analyze video or camera input.

**Quickstart (Windows)**

- **Prerequisites:** Python 3.10+ recommended, git, and a webcam (optional).
- **Create venv and activate:**

```powershell
python -m venv .venv
& .venv\Scripts\Activate.ps1
```

- **Install dependencies:**

```powershell
pip install -r backend/requirements.txt
```

- **Run backend (example):**

```powershell
cd backend
python app/main.py
```

- **Run tests:**

```powershell
cd backend
pytest -q
```

**Repository Structure (top-level)**

- **backend/**: Python backend, models, tests and scripts.
  - **app/**: Main application code organized by concern (biomechanics, assessment, feedback, repetition, scoring, services, utils).
  - **requirements.txt**: Python dependencies for backend.
  - **test_camera.py**, **test_video.py**: Example tests.
  - **yolo11n-pose.pt**: Pose model file used by the backend (tracked in repo).
- **frontend/**: Front-end assets (if present) and integration points.
- **videos/**: Sample videos and test assets.

**Key modules**

- **app/biomechanics/**: angle calculation, trackers, and feature extraction.
- **app/assessment/**: rule engine, mistake detection, severity and thresholds.
- **app/repetition/**: repetition detector and state tracking.
- **app/feedback/**: feedback generation, summaries, and report generation.
- **app/services/pose_service.py**: Interface to pose estimation model.

**Configuration & Notes**

- The pose model file (yolo11n-pose.pt) should be present in the backend folder. If you replace the model, ensure the path is updated in app/services/pose_service.py or wherever the model loader is configured.
- Camera index, input video path, and other runtime options are typically provided via command-line args or environment variables in app/main.py — check that file for specifics.
- For performance on CPU, consider smaller model variants or a GPU-enabled environment with appropriate drivers and PyTorch/CUDA builds.

**Development**

- Follow standard Python packaging practices. Add new dependencies to backend/requirements.txt.
- Run unit tests via pytest from the backend directory.

**Contributing**

- Open an issue for bugs or feature requests. Create pull requests against the main branch and include tests for new features.

**License & Attribution**

- No license file is included by default — add a LICENSE file if you plan to publish or share under a specific license.

**Contact**

- For questions about the code, check the modules under backend/app and open an issue with a clear reproduction case.

---
Generated README summary for quick onboarding and development.
