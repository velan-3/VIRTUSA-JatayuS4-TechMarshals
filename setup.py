from cx_Freeze import setup, Executable
import sys

# Increase recursion limit if needed (YOLO models can be deep)
sys.setrecursionlimit(3000)

# Detecting platform plugin path dynamically
# venv_dir = os.path.dirname(sys.executable)
# platforms_path = os.path.join(venv_dir, "Lib", "site-packages", "PyQt5", "Qt5", "plugins", "platforms")
# .venv\Lib\site-packages\PyQt5\Qt5\plugins\platforms\qwindows.dll
import torch
import torchvision
import os
# torch_libs = [(os.path.join(os.path.dirname(torch.__file__), item), item) 
#             for item in os.listdir(os.path.dirname(torch.__file__)) 
#             if os.path.isfile(os.path.join(os.path.dirname(torch.__file__), item))]
# Files to include with the build
include_files = [
    ("backend/yolomodels", "backend/yolomodels"),
    ("auth", "auth"),
    ("asset", "asset"),
    ("GrafanaLabs", "GrafanaLabs"),
    ('huggingface',"huggingface"),
    ("static","static"),
    # ("D:/virtusaa/.venv/Lib/site-packages/pyarrow", "pyarrow"),
    ("D:/virtusaa/.venv/Lib/site-packages/PyQt5/Qt5/plugins/platforms", "platforms"),
    # ("D:/virtusaa/VeterinaryAssistant/external/DroidCam.Client.7.1.0.exe", "DroidCam.Setup.6.5.exe") # Required for qwindows.dll
] 

build_exe_options = {
    "packages": [
        "os", "sys", "cv2", "torch", "pymongo", "threading", "requests", "uuid", "time", "datetime",
        "googleapiclient", "google.oauth2", "googleapiclient.discovery", "googleapiclient.http",
        "PyQt5", "PyQt5.QtWidgets", "PyQt5.QtGui", "PyQt5.QtCore",
        "ultralytics", "PIL", "numpy", "concurrent.futures", "io", "mimetypes","httplib2","socks","dns", "dns.rdatatype", "dns.rdtypes", "dns.resolver",
        "joblib", "pickle", "tempfile", "shutil",
        "flask", "werkzeug", "cryptography", "zipfile", "uuid",
        "langchain", "langchain_community.vectorstores", "langchain_huggingface",
        "langchain_mistralai.chat_models", "langchain_core.prompts", "langchain.chains", "langchain.chains.combine_documents",
        "deep_translator", "concurrent.futures", "pandas","pygrabber", "winsound","psutil","chromadb","pyarrow", "comtypes",
        "comtypes.stream","pydantic", "pydantic.typing", "transformers", "tokenizers", "sentence_transformers", 
        "opentelemetry", "opentelemetry.context", "opentelemetry.trace", 
        "packaging","pythoncom", "pywintypes","multiprocessing","sklearn",
        "sklearn.ensemble","sklearn.ensemble._forest",  "sklearn.model_selection","sklearn.preprocessing","sklearn.compose","imblearn","imblearn.over_sampling","joblib",
        "ultralytics.utils.ops",
        "ultralytics.engine.predictor",
        "ultralytics.engine.results",
    ],
    "include_files": include_files,
    "excludes": ["PyQt5.QtQml",
    "PyQt5.QtQuick",
    "PyQt5.QtQuickWidgets"],
    "include_msvcr": True, # include Visual C++ redistributables
}
executables = [
    Executable(
        "main.py",
        base="Win32GUI",  # Use "None" for console mode, "Win32GUI" for GUI mode
        target_name="VeterinaryAssistant.exe",
        icon = "static/favicon.ico"
    )
]

setup(
    name="Veterinary Assistant",
    version="0.1",
    description="Cattle Disease Detection(offline + online)",
    options={"build_exe": build_exe_options},
    executables=executables
)
