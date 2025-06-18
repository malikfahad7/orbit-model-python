import cv2
from ultralytics import YOLO
from datetime import datetime
import requests
import uuid
import cloudinary
import cloudinary.uploader
import os
import threading
import queue
import logging
import time
from flask import Flask, Response
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Cloudinary
cloudinary.config(
    cloud_name='doe01tx5g',
    api_key='913455577595659',
    api_secret='VsL-Zm_6T4xsykaXVp4oGOeUrIU'
)

API_URL = 'https://orbit-ivory.vercel.app/api/suspiciousActivity/activity'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
@app.route('/')
def index():
    return "Gun Detection Model is running!"
# Global variables
frame_queue = queue.Queue(maxsize=10)
upload_queue = queue.Queue()
stop_event = threading.Event()
model = YOLO('./runs/detect/Normal_Compressed/weights/best.pt')
video_capture = None
width, height = 416, 416
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter("detected_objects_live.mp4", fourcc, 20.0, (width, height))

def send_detection_data(suspicious_id, floor_no, camera_no, image_url, detection_type):
    detection_data = {
        'SuspiciousActivityId': suspicious_id,
        'FloorNo': floor_no,
        'CameraNo': camera_no,
        'Type': detection_type,
        'Image': image_url
    }
    try:
        response = requests.post(API_URL, json=detection_data, timeout=5)
        if response.status_code == 201:
            logging.info("Suspicious activity reported: %s", response.json())
        else:
            logging.error("Failed to report suspicious activity. Error: %s", response.json())
    except requests.RequestException as e:
        logging.error("Error sending detection data: %s", e)

def upload_to_cloudinary(image_path, suspicious_id):
    date_folder = datetime.now().strftime("%d-%m-%Y")
    public_id = f"{date_folder}/{suspicious_id}"
    try:
        response = cloudinary.uploader.upload(
            image_path,
            public_id=public_id,
            resource_type="image",
            timeout=10
        )
        return response['secure_url']
    except Exception as e:
        logging.error("Error uploading to Cloudinary: %s", e)
        return None

def cloudinary_upload_worker():
    while not stop_event.is_set():
        try:
            screenshot, suspicious_id, floor_no, camera_no, detection_type = upload_queue.get(timeout=1)
            image_url = upload_to_cloudinary(screenshot, suspicious_id)
            if image_url:
                send_detection_data(suspicious_id, floor_no, camera_no, image_url, detection_type)
            os.remove(screenshot)
            upload_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logging.error("Error in upload worker: %s", e)

def capture_frames():
    global video_capture
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|reorder_queue_size;5000|buffer_size;1024000"
    video_capture = cv2.VideoCapture(
        "rtsp://admin:energyCam@192.168.1.200:554/Streaming/Channels/101",
        cv2.CAP_FFMPEG
    )

    if not video_capture.isOpened():
        logging.error("Unable to open video stream.")
        return

    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    while not stop_event.is_set():
        ret, frame = video_capture.read()
        if not ret:
            logging.warning("Failed to read frame from video stream.")
            time.sleep(0.01)
            continue
        try:
            frame_queue.put_nowait(frame)
        except queue.Full:
            pass

def generate_frames():
    alert = False
    frames_since_detection = 0
    frame_count = 0
    skip_frames = 4
    floor_no = 4
    camera_no = 1
    detection_type = ""

    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        frame_count += 1
        if frame_count % skip_frames != 0:
            continue

        frame_resized = cv2.resize(frame, (width, height))
        results = model(frame_resized, conf=0.5, iou=0.7)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = f"{result.names[cls]} {conf:.2f}"
                color = (0, cls * 50 % 255, 255)
                cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame_resized, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                detection_type = result.names[cls]
                alert = True

        out.write(frame_resized)

        if alert:
            frames_since_detection += 1
            if frames_since_detection > 10:
                suspicious_id = str(uuid.uuid4())
                screenshot = f"{suspicious_id}.jpg"
                cv2.imwrite(screenshot, frame_resized)
                upload_queue.put((screenshot, suspicious_id, floor_no, camera_no, detection_type))
                frames_since_detection = 0
                alert = False

        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask_app():
    app.run(host='0.0.0.0', port=8000, threaded=True)

if __name__ == '__main__':
    try:
        threading.Thread(target=cloudinary_upload_worker, daemon=True).start()
        threading.Thread(target=capture_frames, daemon=True).start()
        start_flask_app()
    except KeyboardInterrupt:
        stop_event.set()
        if video_capture:
            video_capture.release()
        out.release()
        cv2.destroyAllWindows()
        upload_queue.join()
