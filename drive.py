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

# def resource_path(relative_path):
#         # try:
#         #     base_path = sys._MEIPASS  # PyInstaller
#         # except AttributeError:
#         #     base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
#         # return os.path.join(base_path, relative_path)
#         return os.path.abspath(relative_path)
    
# def decrypt_to_memory(enc_path):
#     FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte base64-encoded key

#     fernet = Fernet(FERNET_KEY)
#     with open(resource_path(enc_path), "rb") as f:
#         encrypted_data = f.read()
#     decrypted_data = fernet.decrypt(encrypted_data)

#     # Write to a temp file
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pickle")
#     temp_file.write(decrypted_data)
#     temp_file.close()
#     temp_dir = os.path.dirname(temp_file.name)
#     register_temp_dir(temp_dir)
#     return temp_file.name 


# class DriveUploader:

    
#     def __init__(self):
#         self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
#         self.creds = None
#         self.token_path = decrypt_to_memory(resource_path('auth/token.pickle.enc'))
#         self.secret_path = decrypt_to_memory(resource_path('auth/credentials.json.enc'))

#         if os.path.exists(self.token_path):
#             with open(self.token_path, 'rb') as token:
#                 self.creds = pickle.load(token)

#         if not self.creds or not self.creds.valid:
#             if self.creds and self.creds.expired and self.creds.refresh_token:
#                 try:
#                     self.creds.refresh(Request())
#                 except Exception as e:
#                     flow = InstalledAppFlow.from_client_secrets_file(
#                     self.secret_path, self.SCOPES)
#                     self.creds = flow.run_local_server(port=0)
#                     with open(self.token_path, 'wb') as token:
#                         pickle.dump(self.creds, token)
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.secret_path, self.SCOPES)
#                 self.creds = flow.run_local_server(port=0)
#                 with open(self.token_path, 'wb') as token:
#                     pickle.dump(self.creds, token)

#         self.drive_service = build('drive', 'v3', credentials=self.creds)
import os
import pickle
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Constants ---
FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # Replace with your Fernet key
fernet = Fernet(FERNET_KEY)

# --- Utility Functions ---
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
            
# # a = DriveUploader()
# # a.upload_image_to_drive('D:/virtusaa/1m.jpeg','1CP4pvN00v_nxsaILaauQWKpAMXzzRe5H')

# import io
# import os
# import sys
# import mimetypes
# import tempfile
# import uuid
# import pickle
# from pathlib import Path
# from PIL import Image
# from cryptography.fernet import Fernet
# from google.oauth2 import service_account
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload
# from temptrack import register_temp_dir

# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS  # for cx_Freeze or PyInstaller
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

# FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte key


# def decrypt_to_memory(enc_path, suffix=".temp"):
#     fernet = Fernet(FERNET_KEY)
#     with open(resource_path(enc_path), "rb") as f:
#         encrypted_data = f.read()
#     decrypted_data = fernet.decrypt(encrypted_data)

#     # Write decrypted data to temp file
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
#     temp_file.write(decrypted_data)
#     temp_file.close()

#     # Register for cleanup
#     register_temp_dir(os.path.dirname(temp_file.name))
#     return temp_file.name


# def encrypt_token_to_file(token_obj, dest_path):
#     fernet = Fernet(FERNET_KEY)
#     pickled = pickle.dumps(token_obj)
#     encrypted = fernet.encrypt(pickled)

#     with open(dest_path, 'wb') as f:
#         f.write(encrypted)


# class DriveUploader:
#     def __init__(self):
#         self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
#         self.creds = None

#         # Decrypt credentials.json.enc and (if exists) token.pickle.enc
#         self.secret_path = decrypt_to_memory('auth/credentials.json.enc', suffix=".json")

#         self.token_enc_path = resource_path('auth/token.pickle.enc')
#         if os.path.exists(self.token_enc_path):
#             self.token_path = decrypt_to_memory('auth/token.pickle.enc', suffix=".pickle")
#             with open(self.token_path, 'rb') as token:
#                 self.creds = pickle.load(token)

#         # Handle token refresh or first-time auth
#         if not self.creds or not self.creds.valid:
#             if self.creds and self.creds.expired and self.creds.refresh_token:
#                 try:
#                     self.creds.refresh(Request())
#                 except Exception as e:
#                     print(f"Token refresh failed: {e}")
#                     self.creds = self.do_login()
#             else:
#                 self.creds = self.do_login()

#             # Encrypt and save token
#             encrypt_token_to_file(self.creds, self.token_enc_path)

#         self.drive_service = build('drive', 'v3', credentials=self.creds)

#     def do_login(self):
#         flow = InstalledAppFlow.from_client_secrets_file(self.secret_path, self.SCOPES)
#         return flow.run_local_server(port=0)

#     def upload_image_to_drive(self, image, folder_id):
#         if isinstance(image, Image.Image):
#             image_buffer = io.BytesIO()
#             image.save(image_buffer, format='JPEG')
#             image_buffer.seek(0)
#             mimetype = 'image/jpeg'
#         elif isinstance(image, str) and os.path.exists(image):
#             mimetype = mimetypes.guess_type(image)[0] or 'application/octet-stream'
#             with open(image, 'rb') as f:
#                 image_buffer = io.BytesIO(f.read())
#         else:
#             image_buffer = io.BytesIO(image)
#             mimetype = 'image/jpeg'

#         media = MediaIoBaseUpload(image_buffer, mimetype=mimetype)

#         file_metadata = {
#             'name': str(uuid.uuid4()) + '.jpg',
#             'parents': [folder_id]
#         }

#         try:
#             file = self.drive_service.files().create(
#                 body=file_metadata, media_body=media, fields='id'
#             ).execute()
#             print('Image uploaded. File ID:', file.get('id'))
#         except Exception as e:
#             print('Upload failed:', e)
