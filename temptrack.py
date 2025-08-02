import os
import shutil
import time

TEMP_DIRS = []
CHROMA_OBJECTS = []

def register_temp_dir(temp_dir, chroma_obj=None):
    """Register a temporary directory and optional Chroma object for cleanup"""
    if temp_dir and temp_dir not in TEMP_DIRS:
        TEMP_DIRS.append(temp_dir)
    if chroma_obj:
        CHROMA_OBJECTS.append(chroma_obj)

def cleanup_temp_dirs():
    """Clean up temporary directories and Chroma objects"""
    # First close Chroma connections
    for obj in CHROMA_OBJECTS:
        try:
            print(f"[temptrack] Closing Chroma connection: {obj}")
            if hasattr(obj, '_client'):
                obj._client.close()
            obj = None
        except Exception as e:
            print(f"[temptrack] Error closing Chroma: {e}")

    # Wait a moment for connections to close
    time.sleep(1)

    # Then clean up directories
    for temp_dir in TEMP_DIRS:
        try:
            if os.path.exists(temp_dir):
                if os.path.isfile(temp_dir):
                    os.unlink(temp_dir)
                else:
                    # Try multiple times with delays
                    for attempt in range(3):
                        try:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            break
                        except Exception as e:
                            if attempt < 2:
                                time.sleep(1)
                            else:
                                print(f"[Cleanup Error] {temp_dir}: {e}")
        except Exception as e:
            print(f"[Cleanup Error] {temp_dir}: {e}")

    TEMP_DIRS.clear()
    CHROMA_OBJECTS.clear()
