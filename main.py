import sys,os
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,  QMessageBox

)
from PyQt5.QtGui import QImage, QPixmap
from model2 import Model
from sqlite import SQLiteManager
from datetime import datetime
from drive import DriveUploader
import winsound
import numpy as np
import time
from pygrabber.dshow_graph import FilterGraph
import subprocess
import warnings
import psutil
import tempfile
import pythoncom
from cryptography.fernet import Fernet
from temptrack import cleanup_temp_dirs
import shutil
warnings.filterwarnings("ignore", category=DeprecationWarning)


def resource_path(relative_path):
    # try:
    #     base_path = sys._MEIPASS
    # except AttributeError:
    #     base_path = os.path.abspath(".")
    # return os.path.join(base_path, relative_path)
    return os.path.abspath(relative_path)
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = resource_path("platforms")

class LedIndicator(QWidget):
    def __init__(self, label_text):
        super().__init__()

        self.label = QLabel(label_text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.side_length = 10  # Reduced the size of the indicators
        self.led_radius = 9  # Reduced the radius of the indicators
        self.setMinimumSize(self.led_radius * 2, self.led_radius * 2)
        #self.status = False  # Initial status
        self.color = "#FFFFFF"
        
    def set_status(self, status):
        self.status = status
        if self.status:
            self.color = "#FF6347"  # red if disease is detected
        else:
            self.color = "#32CD32"  # green if no disease is detected
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))
        painter.drawEllipse(self.rect().center(), self.led_radius, self.led_radius)


class VideoViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

        # Video processing variables
        self.video_thread = None
        self.model = Model()
        self.mongo = SQLiteManager()
        self.drive =  DriveUploader()
    def toggle_video_processing(self):
        if self.toggle_button.isChecked():
            # Start detection
            self.toggle_button.setText("Stop Detection")
            self.toggle_button.setStyleSheet("background-color: red; color: white; font-size: 14px;")
            self.start_video_processing()
        else:
            # Stop detection
            self.toggle_button.setText("Start Detection")
            self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
            self.stop_video_processing()


    def setupUi(self):
        self.setObjectName("UVA")
        self.resize(877, 686)
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 851, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("VeneerW01-Two")
        font.setPointSize(34)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # Adjusted geometry for videoFrame and progressBar
        self.videoFrame = QtWidgets.QLabel(self)
        self.videoFrame.setGeometry(QtCore.QRect(10, 100, 480, 531))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        self.videoFrame.setFont(font)
        self.videoFrame.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.videoFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.videoFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.videoFrame.setObjectName("videoFrame")
        
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(610, 340, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("color: white;")

        
        self.bcs_label = QtWidgets.QLabel(self)
        self.bcs_label.setGeometry(QtCore.QRect(490, 200, 400, 50))  
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(13)  
        font.setBold(True)
        self.bcs_label.setFont(font)
        self.bcs_label.setObjectName("bcs_label")
        self.bcs_label.setStyleSheet("color: white;")
        self.bcs_label.setAlignment(QtCore.Qt.AlignCenter)
        self.bcs_label.setText("Body Condition Score: Not Available")
        
        # Adding colored circles before disease names
        self.circle_indicator_1 = LedIndicator("Lumpy Skin Disease")
        self.circle_indicator_1.setGeometry(QtCore.QRect(580, 350, 20, 20))
        self.circle_indicator_1.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")# Initial status
        self.circle_indicator_1.setParent(self)  # Set VideoViewer as the parent

        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(610, 390, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_3.setStyleSheet("color: white;")

        # Adding colored circles before disease names
        self.circle_indicator_2 = LedIndicator("Mouth Disease")
        self.circle_indicator_2.setGeometry(QtCore.QRect(580, 400, 20, 20))
        self.circle_indicator_2.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")  # Initial status
        self.circle_indicator_2.setParent(self)  # Set VideoViewer as the parent
        
        self.toggle_button = QtWidgets.QPushButton("Start Detection", self)
        self.toggle_button.setGeometry(QtCore.QRect(600, 480, 180, 40))
        self.toggle_button.setCheckable(True)
        self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.toggle_button.clicked.connect(self.toggle_video_processing)
        
        self.vetai_button = QtWidgets.QPushButton("VETAI", self)
        self.vetai_button.setGeometry(QtCore.QRect(600, 530, 180, 40))  # just below
        self.vetai_button.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 14px;"
        )
        self.vetai_button.clicked.connect(self.askai)



        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "AVA"))
        self.label.setText(_translate("Dialog", "AI VETERINARY ASSISTANT"))
        self.label_2.setText(_translate("Dialog", "Lumpy Skin Disease"))
        self.label_3.setText(_translate("Dialog", "Mouth Disease"))
        self.bcs_label.setText(_translate("Dialog", "Body Condition Score: NIL"))

    def update_bcs(self, bcs_score):
        if bcs_score not in ['False', "", None, '[]']:
            leng = len(bcs_score)
            self.bcs_label.setText(f"Body Condition Score: {bcs_score[2:leng-2]}")

    def start_video_processing(self):
        self.video_thread = VideoProcessingThread(self.mongo, self.model, self.drive)
        self.video_thread.frame_processed.connect(self.update_video_frame)
        self.video_thread.disease_detected_updated.connect(self.disease_detected_updated)
        self.video_thread.bcs_updated.connect(self.update_bcs)
        self.video_thread.camera_error_signal.connect(self.handle_camera_error)
        self.video_thread.start()

    def stop_video_processing(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None
            
    def askai(self):
        
        website_link = "http://127.0.0.1:5000/"  

        QtGui.QDesktopServices.openUrl(QtCore.QUrl(website_link))
        
    def handle_camera_error(self):
        QMessageBox.critical(self, "Camera Error", "No working camera found by Iriun.")
        self.toggle_button.setChecked(False)
        self.toggle_button.setText("Start Detection")
        self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")

    def update_video_frame(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        self.videoFrame.setPixmap(pixmap)

    def disease_detected_updated(self, is_lumpy_skin, is_mouth_disease):
        self.circle_indicator_1.set_status(is_lumpy_skin)
        self.circle_indicator_2.set_status(is_mouth_disease)
        
            
    def closeEvent(self, event):
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()
        event.accept()

class VideoProcessingThread(QtCore.QThread):
    frame_processed = QtCore.pyqtSignal(QImage)
    progress_updated = QtCore.pyqtSignal(int)
    disease_detected_updated = QtCore.pyqtSignal(bool, bool)
    bcs_updated = QtCore.pyqtSignal(str)
    camera_error_signal = QtCore.pyqtSignal()

    def __init__(self, mongo, model, drive):
        super().__init__()
        #'1oa5WRfR_g9LXvy1Lw3Lnh8AxUL-T42Lk'
        # 1QS1ilEB_Zyeux5z00-sJPqM4s5xUrvBU'
        self.model = model
        self.mongo = mongo
        self.drive = drive
        self.lumpyid = '1CP4pvN00v_nxsaILaauQWKpAMXzzRe5H'
        self.mouthid = '1WyvXEcFaqVgFDeHiK4neAFbEK_jkq_AS'
        self.bcsid = '1YLefVHSPCewswO8Wps5CVtFVLn0Vu4aZ'
        self._running = True
        self.ll = []
        self.mm = []
        self.lc = 0
        self.mc = 0
        self.bc = 0
        self.timeout_duration = 5  # timeout duration as for not disease affected
        self.last_detection_time = time.time()
        self.green_timeout_duration = 10  # duration after which LED turns green
        self.last_green_update_time = time.time()
        self.lumpy_detection_count =0
        self.mouth_detection_count = 0
        self.bcs_detection_count = 0
        self.upload_threshold = 5 
        self.count=0
        self.frame_buffer_limit=2
    
    def get_camera_index(self):
        pythoncom.CoInitialize()
        try:
            graph = FilterGraph()
            devices = graph.get_input_devices()
            devices.reverse()
            print(devices)
            for i, name in enumerate(devices):
                if "Iriun" in name:
                    return i
        except Exception as e:
                print(f"Device listing error: {e}")
        return -1

            
    
    def validate_droidcam_stream(self,capture, max_attempts=5):
        for attempt in range(max_attempts):
            ret, frame = capture.read()
            if not ret or frame is None:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_val = cv2.mean(gray)[0]
            std_val = np.std(gray)
            
            # Valid frame should have reasonable brightness and variation
            if mean_val > 8 and std_val > 10:
                return True
            
            time.sleep(0.2)  # Wait a bit between attempt
        return False
    
    def run(self):
        camera = self.get_camera_index()
        print(camera)
        if camera == -1:
            self.camera_error_signal.emit()
            return
        cap = cv2.VideoCapture(camera)
        
        if not cap.isOpened():
            self.camera_error_signal.emit()
            return
        
        if not self.validate_droidcam_stream(cap):
            cap.release()
            self.camera_error_signal.emit()
            return
        
        start_time = time.time()
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)
        
        if not fps or fps == 0:
            fps = 30
        frame_interval = 1.0 / fps
        
        if not cap.isOpened():
            self.camera_error_signal.emit()
            print("Error: Could not open camera.")
            return


        while self._running:
            ret, frame = cap.read()
            if not ret:
                break

            self.progress_updated.emit(0)

            index = self.model.compute_disease(frame)
            # print(index)
            
            # Detection Check
            if index is not None and index != ([], [], []):
                if index[0] == ['Brown_lumpy']:
                    # self.ll.append(frame)
                    print('lumpy')
                    self.lumpy_detection_count += 1
                    
                    if self.lumpy_detection_count == self.upload_threshold:
                        # Upload limited frames to drive
                        self.disease_detected_updated.emit(True, False)
                        winsound.Beep(1000, 200) 
                        for image_data in self.model.lumpy_frame[:self.frame_buffer_limit]:
                            image = image_data
                            self.drive.upload_image_to_drive(image, self.lumpyid)

                        # Log and reset
                        self.lc += 1
                        self.mongo.insert_document({
                            'date': datetime.now().date().isoformat(),
                            'lumpy_skin_count': self.lc,
                            'mouth_disease_count': self.mc,
                            'BCS': self.bc
                        })
                        self.disease_detected_updated.emit(False, False)
                        self.model.lumpy_frame.clear()
                        self.model.lumpy_skin_count = 0
                        self.lumpy_detection_count = 0

                    

                elif index[1] == ['Mouth Disease Infected']:
                    print("mouth")
                    # self.mm.append(frame)
                    self.mouth_detection_count += 1
                    if self.mouth_detection_count == self.upload_threshold:
                        self.disease_detected_updated.emit(False, True)
                        winsound.Beep(1200, 200)
                        for image_data in self.model.mouth_frame[:self.frame_buffer_limit]:
                            image =  image_data                                                                 
                            self.drive.upload_image_to_drive(image, self.mouthid)

                        self.mc += 1
                        self.mongo.insert_document({
                            'date': datetime.now().date().isoformat(),
                            'lumpy_skin_count': self.lc,
                            'mouth_disease_count': self.mc,
                            'BCS': self.bc
                        })
                        self.disease_detected_updated.emit(False, False)
                        self.model.mouth_frame.clear()
                        self.model.mouth_disease_count = 0
                        self.mouth_detection_count = 0
                        
                elif index[2]:
                    print("BCS")
                    # self.mm.append(frame)
                    self.bcs_detection_count += 1
                    print(self.bcs_detection_count)
                    if self.bcs_detection_count == 5:
                        # self.upload_threshold(str(index[2]))
                        bcs = str(index[2])
                        winsound.Beep(800, 200)
                        self.bcs_updated.emit(bcs)
                        # self.disease_detected_updated.emit(False, True)
                        
                        for image_data in self.model.bcs_frame[:self.frame_buffer_limit]:
                            image = image_data                                                               
                            self.drive.upload_image_to_drive(image, self.bcsid)

                        self.bc += 1
                        self.mongo.insert_document({
                            'date': datetime.now().date().isoformat(),
                            'lumpy_skin_count': self.lc,
                            'mouth_disease_count': self.mc,
                            'BCS': self.bc
                        })
                        self.disease_detected_updated.emit(False, False)
                        self.model.bcs_frame.clear()
                        self.model.b_s = 0
                        self.bcs_detection_count = 0


            else:
                if self.model.lumpy_skin_count==0 or self.model.mouth_disease_count==0:
                        self.disease_detected_updated.emit(False, False)
                
    
            # if len(index) >= 3 and isinstance(index[2], (str, int, float)):
            #     bcs = str(index[2])
            #     if self.model.b_s > 3:
            #         self.bcs_updated.emit(bcs)

            # Display live frame
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb_image.shape
            qimage = QImage(rgb_image.data, width, height, channels * width, QImage.Format_RGB888)
            self.frame_processed.emit(qimage)

            # Upload & DB Insertion every N seconds or every M frames
    
            # Adjust frame rate
            time_taken = time.time() - start_time
            delay = max(frame_interval - time_taken, 0)
            time.sleep(delay)
            start_time = time.time()

        cap.release()
    def stop(self):
        self._running = False


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    qt_app = QtWidgets.QApplication(sys.argv)
    window = VideoViewer()
    palette = QtGui.QPalette()
    background_image = QPixmap(resource_path("asset/1594429_11593.jpg") ) 
    background_image = background_image.scaled(window.size(), QtCore.Qt.IgnoreAspectRatio)    
    palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(background_image))
    palette.setColor(
        QtGui.QPalette.WindowText, QtGui.QColor("#0FD343")
    )  # Neon blue text
    palette.setColor(
        QtGui.QPalette.ButtonText, QtGui.QColor("#014f15")
    )  # Dark blue button text
    window.setPalette(palette)
    window.show()
    import threading
    
    def start_flask():
        from app import FlaskAppRunner
        a = FlaskAppRunner()
        a.run()
    def get_temp_grafana_dir():
        return os.path.join(os.getenv("TEMP"), "VeterinaryAssistant", "grafana")

    def copy_grafana_to_temp():
        temp_grafana_dir = get_temp_grafana_dir()
        try:
            src = resource_path("GrafanaLabs")
            shutil.copytree(src, temp_grafana_dir)
            return temp_grafana_dir
        except Exception as e:
            print("Already present")
            print(temp_grafana_dir)
        return temp_grafana_dir
    
    def start_grafana():
        grafana_dir = copy_grafana_to_temp()
        grafana_exe = os.path.join(grafana_dir, "bin", "grafana-server.exe")
        config_path = os.path.join(grafana_dir, "conf", "custom.ini")
        # grafana_path = os.path.join("GrafanaLabs", "bin", "grafana-server.exe")
        # config_path = os.path.join("GrafanaLabs", "conf", "custom.ini")
        
            
        global grafana_process
        env = os.environ.copy()
        env["TEMP"] = os.environ["TEMP"]
        print(env["TEMP"])
        try:
            grafana_process = subprocess.Popen([
                grafana_exe,
                f"--config={config_path}",
                f"--homepath={grafana_dir}" ,
                "--packaging=standalone"
            ],
            env=env,
            bufsize=1,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        except Exception as e:
            print("Already Present")
            
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=start_grafana, daemon=True).start()
    

    
    def kill_process_tree(pid):
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        
    def on_exit():
        if 'grafana_process' in globals() and grafana_process.poll() is None:
            kill_process_tree(grafana_process.pid)
        cleanup_temp_dirs()
    
    qt_app.aboutToQuit.connect(on_exit)
    sys.exit(qt_app.exec_())
    