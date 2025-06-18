# Gun Detection Model (YOLO + Flask + Cloudinary)

This project is a **real-time object detection system** using the **YOLO model** with an **RTSP camera feed**, backed by **Flask** for web serving and **Cloudinary** for image uploads. Detected images and details are reported to a remote API.

---

## Dependencies

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


## Run the App

To start the detection system, run:

```bash
python detecting-images.py
```

---

## Cloud Upload & API Report

When a suspicious object is detected:
- A screenshot is saved.
- It is uploaded to Cloudinary.
- The detection data is POSTed to a remote API.

---

## Stop the App

Use `Ctrl + C` in the terminal. This will:
- Stop the RTSP capture.
- Release the video writer.
- Safely shutdown the upload queue.

---

## Notes

- Video is saved locally as: `detected_objects_live.mp4`
- Images are uploaded to Cloudinary with the format: `dd-mm-yyyy/UUID.jpg`
