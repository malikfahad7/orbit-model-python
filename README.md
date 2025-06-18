# 🔍 Suspicious Activity Detection System

This project uses **YOLOv8** (Ultralytics), **OpenCV**, and **Cloudinary** to detect suspicious objects (e.g., weapons) in real-time from a webcam feed and report them via API with image evidence.

---

## 📦 How to Install Dependencies

Make sure you have Python 3.8+ installed.

1. Clone the repository or download the code.
2. Navigate to the project directory.
3. Run the following command to install all dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 How to Run

To start detection using the webcam, run:

```bash
python detecting-images.py
```

## 🚀 How to  Switch form laptopt camera to IP Camera

By default, the system uses your laptop webcam:
```bash
video_capture = cv2.VideoCapture(0)
```
To use an IP camera feed, replace that line with:
```bash
# Replace with your actual IP camera stream URL
ip_camera_url = 'http://192.168.1.100:8080/video'  # or use rtsp://...
video_capture = cv2.VideoCapture(ip_camera_url)
```

Detected suspicious activities (e.g., "Knife", "Gun") will:

> Be highlighted in the live video.

> Trigger a snapshot after a short delay.

> Upload the snapshot to Cloudinary.

> Send detection data to your backend API.
