# AI PhotoBox - Jetson AGX Orin

An interactive photo booth with AI image processing, based on NVIDIA Jetson AGX Orin Development Kit.

## 🎯 Project Goal

Development of a standalone photo booth that:
- Captures photos with webcam
- Shows live preview during countdown
- Processes images artistically with AI (e.g. astronaut, superhero)
- Optionally prints photos (Canon SELPHY CP1500)
- Works completely offline
- Provides images for download via local hotspot

## 🛠️ Hardware

- **Computer:** NVIDIA Jetson AGX Orin Development Kit
- **Camera:** USB Webcam (1920x1080)
- **Display:** Touchscreen for operation
- **Input:** Zero Delay Encoder (Arcade button)
- **Printer:** Canon SELPHY CP1500 (wired connection)

## 📦 Tech Stack

### Backend
- **Python 3.10** with Flask
- **OpenCV** for camera control
- **PyTorch** for AI inference (planned)
- Filesystem-based image storage (no database)

### Frontend
- **HTML/CSS/JavaScript** (Single Page Application)
- Runs in browser (Chromium Kiosk mode)
- Touch-optimized interface

### Planned AI Integration
- Stable Diffusion xl for image transformations
- Optimized for Jetson GPU (CUDA/TensorRT)

## 🚀 Current Status

### ✅ Implemented (Milestone 1)

- Flask web server with REST API
- Webcam integration with live preview
- Photo capture with 5-4-3-2-1 countdown
- Responsive web interface
- Camera buffer optimization for fresh frames
- Cache-busting for correct image refresh
- Temporary image storage in `static/photos/`

### 🔄 In Progress

- **AI Image Processing:** Testingphase SDXL for Jetson
  - Using SD-webui to get a better understanding of prompting
  - Implement SDXL in camera app

### 📋 Planned

- [ ] Stable Diffusion xl Image-to-Image pipeline
- [ ] Effect selection in frontend or at random in backend (Astronaut, Superhero, etc.)
- [ ] Printer integration (Canon SELPHY CP1500)
- [ ] WiFi hotspot for downloads
- [ ] Zero Delay Encoder button integration
- [ ] Auto-cleanup of old photos
- [ ] Kiosk mode setup

## 🤝 Development

This project is in active development.
