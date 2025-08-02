import cv2, os, sys
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
from io import BytesIO
from cryptography.fernet import Fernet
import tempfile
from temptrack import register_temp_dir

FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte base64-encoded key

fernet = Fernet(FERNET_KEY)

def decrypt_file_to_bytesio(enc_path):
    # with open(resource_path(enc_path), 'rb') as f:
    #     encrypted = f.read()
    # decrypted = cipher.decrypt(encrypted)
    # return io.BytesIO(decrypted)
    with open(enc_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = Fernet(FERNET_KEY).decrypt(encrypted_data)

    # Create temp file with .pt extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pt')
    temp_file.write(decrypted_data)
    temp_file.flush()
    temp_file.close()
    temp_dir = os.path.dirname(temp_file.name)
    register_temp_dir(temp_dir)
    return temp_file.name  

def resource_path(relative_path):
        # try:
        #     base_path = sys._MEIPASS  # Cx_freeze
        # except AttributeError:
        #     base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        # return os.path.join(base_path, relative_path)
        return os.path.abspath(relative_path)
# ---------------------------- model class ------------------------
class ImageDiseaseModel:
    """Single‑image inference for Lumpy Skin, Mouth Disease and BCS."""

    def __init__(self):
        self.ld    = YOLO(decrypt_file_to_bytesio(resource_path("backend/yolomodels/lumpy.pt.enc")),verbose=False)
        self.mouth = YOLO(decrypt_file_to_bytesio(resource_path("backend/yolomodels/mouth.pt.enc")),verbose=False)
        self.bcs   = YOLO(decrypt_file_to_bytesio(resource_path("backend/yolomodels/bcs.pt.enc")),verbose=False)
        self.executor = ThreadPoolExecutor(max_workers=3)  # run 3 YOLOs in parallel

    # -----------------------------------------------------------------
    def detect_image(self, image_bytes: bytes):
        
        # 1) bytes → OpenCV BGR ndarray (what VideoCapture delivers)
        buf   = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Invalid image file")

        # 2) prepare inputs
        rgb_pil   = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        # rgb_pil.show()
        gray_pil  = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        # 3) threaded inference
        fut_ld    = self.executor.submit(self.ld,    gray_pil, verbose=False,imgsz=640,stream=True)
        fut_mouth = self.executor.submit(self.mouth, rgb_pil, classes=[1], verbose=False,stream=True)
        fut_bcs   = self.executor.submit(self.bcs,   rgb_pil,  verbose=False,imgsz=640,stream=True)

        lumpy_det = self._post(fut_ld.result(),    self.ld.names,    0.55)
        mouth_det = self._post(fut_mouth.result(), self.mouth.names, 0.30)
        bcs_det   = self._post(fut_bcs.result(),   self.bcs.names,   0.50)

        diseases = []
        if lumpy_det: diseases.append("Lumpy Skin Disease")
        if mouth_det: diseases.append("Mouth Disease")

        # 4) Build JSON‑ready result
        return {
            "diseases": diseases,
            "bcs": float(bcs_det[0]) if bcs_det else None   # assuming class name is score str
        }

    # -----------------------------------------------------------------
    @staticmethod
    def _post(results, class_names, conf_th):
        """
        returns [] or [detected_label]  (highest‑confidence box only)
        """
        for r in results:
            boxes = r.boxes.cpu().numpy()
            if boxes:
                best_idx = int(np.argmax(boxes.conf))
                if float(boxes.conf[best_idx]) >= conf_th:
                    return [class_names[int(boxes.cls[best_idx])]]
        return []

# ---------------------------- usage in Flask ----------------------
# (inside your /upload_img route)
# img_bytes = file.read()
# detector  = ImageDiseaseModel()   # ideally instantiate once, not per request
# result    = detector.detect_image(img_bytes)
# return jsonify(result)
