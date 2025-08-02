import cv2,sys,os,io
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()
from ultralytics import YOLO
import io
from cryptography.fernet import Fernet
import tempfile
import joblib
from temptrack import register_temp_dir


# Set this securely in code or use environment variables
FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte base64-encoded key

fernet = Fernet(FERNET_KEY)

def decrypt_file_to_bytesio(enc_path):
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
        
        return os.path.abspath(relative_path)

def load_encrypted_model(filepath):
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    buffer = io.BytesIO(decrypted_data)
    return joblib.load(buffer)


class Model:

    SLOW_STRIDE     = 20   # normal skip 
    FAST_STRIDE     = 5    # stride while disease just detected
    COOLDOWN_FRAMES = 50  
    Reset = 20 # healthy frames before relaxing stride

    def __init__(self) -> None:
        self.ld    = YOLO(decrypt_file_to_bytesio('backend/yolomodels/lumpy.pt.enc'))
        self.mouth = YOLO(decrypt_file_to_bytesio('backend/yolomodels/mouth.pt.enc'))
        self.bcs   = YOLO(decrypt_file_to_bytesio('backend/yolomodels/bcs.pt.enc'))
        self.lumpy_frame = []
        self.mouth_frame = []
        self.bcs_frame =  []
        
        # Thread Declaration
        self.executor = ThreadPoolExecutor(max_workers=3)
        # adaptive‑stride state
        self.frame_idx    = 0
        self.stride       = self.SLOW_STRIDE
        self.cooldown_cnt = 0

        # counters for UI / DB
        self.lumpy_skin_count   = 0
        self.mouth_disease_count = 0
        self.b_s = 0
        
        # self.empty_streak = 0 
        self.lumpy_streak = 0
        self.mouth_streak = 0
        self.bcs_streak   = 0
        self.RESET_AFTER  = 10
        
    def compute_disease(self, image):
        """ Returns (lumpy_detected_list , mouth_detected_list , bcs_detected_list)or (False, False, False) when this frame is skipped."""
        run_inference = (self.frame_idx % self.stride == 0)
        self.frame_idx += 1

        if not run_inference:
            return False, False, False

        # threaded inference 
        gray_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        image = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        # cv2.COLOR_BGR

        fut_ld    = self.executor.submit(self.ld,    image, verbose=False,conf =0.70, task='detect',imgsz=640)
        fut_mouth = self.executor.submit(self.mouth, gray_pil,    verbose=False, classes=[1],conf=0.30, task='detect',imgsz=640)
        fut_bcs   = self.executor.submit(self.bcs,   image,    verbose=False, conf = 0.40,  task='detect',imgsz=640)
        
        lumpy_det   = self._post(fut_ld.result(),    self.ld.names,   0.70)
        mouth_det   = self._post(fut_mouth.result(), self.mouth.names,0.30)
        bcs_det     = self._post(fut_bcs.result(),   self.bcs.names,  0.40)

        disease_now = bool(lumpy_det or mouth_det)
        if lumpy_det:
            self.lumpy_frame.append(image)
        if mouth_det:
            self.mouth_frame.append(image)
        if bcs_det:
            self.bcs_frame.append(image)
            
        #  update counts 
        self.lumpy_skin_count   += len(lumpy_det)
        self.mouth_disease_count += len(mouth_det)
        self.b_s                += len(bcs_det)
        # print(self.b_s)
        # adaptive stride logic 
        if disease_now:
            self.stride = self.FAST_STRIDE
            self.cooldown_cnt = 0
        else:
            self.cooldown_cnt += 1
            if self.cooldown_cnt > self.COOLDOWN_FRAMES and self.stride < self.SLOW_STRIDE:
                self.stride += 5       # 5 → 10 → 15 → 20(Approach demonstration)
                self.cooldown_cnt = 0
                
        if lumpy_det:
            self.lumpy_streak = 0
        else:
            self.lumpy_streak += 1
            if self.lumpy_streak >= self.RESET_AFTER:
                self.lumpy_skin_count = 0
                self.lumpy_frame.clear()
                self.lumpy_streak = 0

        if mouth_det:
            self.mouth_streak = 0
        else:
            self.mouth_streak += 1
            if self.mouth_streak >= self.RESET_AFTER:
                self.mouth_disease_count = 0
                self.mouth_frame.clear()
                self.mouth_streak = 0

        if bcs_det:
            self.bcs_streak = 0
        else:
            self.bcs_streak += 1
            if self.bcs_streak >= self.RESET_AFTER:
                self.b_s = 0
                self.bcs_frame.clear()
                self.bcs_streak = 0

        return lumpy_det, mouth_det, bcs_det

    @staticmethod
    def _post(results, class_names, conf_th):
        """Return list of class names if any box exceeds conf_th else []"""
        detected = []
        for r in results:
            boxes = r.boxes.cpu().numpy()
            if len(boxes):
                best = int(boxes.cls[np.argmax(boxes.conf)])
                if float(boxes.conf.max()) >= conf_th:
                    detected.append(class_names[best])
        return detected

    # optional helper for debugging
    def reset_counts(self):
        self.lumpy_skin_count = 0
        self.mouth_disease_count = 0
        self.b_s = 0
