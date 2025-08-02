import io
import mimetypes
from google.oauth2 import service_account
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import uuid
from PIL import Image
import pickle
import sys,os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from cryptography.fernet import Fernet
from temptrack import register_temp_dir
from pathlib import Path
from cryptography.fernet import Fernet


FERNET_KEY = b''  
fernet = Fernet(FERNET_KEY)

def get_data_dir():
    return os.path.join(os.getenv("LOCALAPPDATA"), "VeterinaryAssistant", "data")

def get_token_path():
    return os.path.join(get_data_dir(), "token.pickle.enc")

def encrypt_pickle_file(data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt_pickle_file(data: bytes) -> bytes:
    return fernet.decrypt(data)

def resource_path(relative_path):
    # Already assumed to be in your project
    try:
        base_path = sys._MEIPASS  # for cx_Freeze
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def decrypt_to_memory(enc_path):
    with open(enc_path, 'rb') as f:
        encrypted = f.read()
    return decrypt_pickle_file(encrypted).decode('utf-8')  # if json string

# --- Main Drive Auth Class ---
class DriveUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None

        os.makedirs(get_data_dir(), exist_ok=True)
        self.token_path = get_token_path()
        print("[DEBUG] Token will be saved to:", get_token_path())

        self.secret_path = decrypt_to_memory(resource_path('auth/credentials.json.enc'))

        # Step 1: Load Token if exists
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token_file:
                    encrypted = token_file.read()
                    decrypted = decrypt_pickle_file(encrypted)
                    self.creds = pickle.loads(decrypted)
            except Exception as e:
                print(f"Failed to load encrypted token: {e}")
                self.creds = None

        # Step 2: Validate or Refresh or Re-auth
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = self._run_flow()
            else:
                self.creds = self._run_flow()

            # Step 3: Save encrypted token
            if self.creds:
                try:
                    with open(self.token_path, 'wb') as token_file:
                        encrypted_data = encrypt_pickle_file(pickle.dumps(self.creds))
                        token_file.write(encrypted_data)
                except Exception as e:
                    print(f"Failed to save encrypted token: {e}")

        # Step 4: Build Drive Service
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def _run_flow(self):
        json_content = self.secret_path  

    # Write it to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json:
            temp_json.write(json_content)
            temp_json_path = temp_json.name

        flow = InstalledAppFlow.from_client_secrets_file(temp_json_path, self.SCOPES)
        return flow.run_local_server(port=0)               
    
    def upload_image_to_drive(self, image, folder_id):
        
        if isinstance(image, Image.Image):
            image_buffer = io.BytesIO()
            image.save(image_buffer, format='JPEG')
            mimetype = 'image/jpeg'
        else:
            try:
                mimetype = mimetypes.guess_type(image)[0]
                with open(image, 'rb') as f:
                    media = MediaIoBaseUpload(f, mimetype=mimetype)
            except TypeError:
                image_buffer = io.BytesIO()
                image_buffer.write(image)
                mimetype = 'image/jpeg'
        
        media = MediaIoBaseUpload(image_buffer, mimetype=mimetype)  # Moved outside try/except to ensure assignment

        file_name = str(uuid.uuid4()) + '.jpg'
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        try:
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print('Image uploaded successfully. File ID:', file.get('id'))
        except Exception as e:
            print(f"Error uploading image: {e}")  # Handle any remaining errors during upload
            

