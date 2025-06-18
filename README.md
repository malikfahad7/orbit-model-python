# Gun Detection Model (YOLO + Flask + Cloudinary)

This project is a **real-time object detection system** (e.g., for detecting guns or other suspicious objects) using the **YOLO model** with an **RTSP camera feed**, backed by **Flask** for web serving and **Cloudinary** for image uploads. Detected images and details are reported to a remote API.

---

## 📦 Dependencies

Make sure you have Python 3.8+ installed. Then install the following dependencies:

```bash
pip install -r requirements.txt
```

### `requirements.txt`

```txt
opencv-python
ultralytics
flask
flask-cors
cloudinary
requests
```

> 💡 `ultralytics` installs YOLOv8 and its required dependencies.

---

## 🔐 Setup Virtual Environment

Use the following commands to set up and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate

# Then install the dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Make sure to update the following sections in your code if needed:

- **Cloudinary Credentials** (in `cloudinary.config`)
- **RTSP Stream URL** (in `capture_frames()` function)
- **YOLO Model Path** (update the `YOLO()` path to your trained model file)
- **API Endpoint** (`API_URL` for reporting detections)

---

## ▶️ Run the App

To start the detection system, run:

```bash
python detecting-images.py
```

---

## 📺 Access Live Feed

Once the server is running, open your browser and visit:

```
http://localhost:8000/video_feed
```

You should see the live annotated video feed with detection boxes.

---

## 📤 Cloud Upload & API Report

When a suspicious object is detected:
- A screenshot is saved.
- It is uploaded to Cloudinary.
- The detection data is POSTed to a remote API.

---

## 🛑 Stop the App

Use `Ctrl + C` in the terminal. This will:
- Stop the RTSP capture.
- Release the video writer.
- Safely shutdown the upload queue.

---

## 📝 Notes

- Video is saved locally as: `detected_objects_live.mp4`
- Images are uploaded to Cloudinary with the format: `dd-mm-yyyy/UUID.jpg`
- Detection occurs every `4` frames (configurable via `skip_frames`)
