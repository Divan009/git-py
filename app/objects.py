import hashlib
import os
import zlib

from app.config import OBJECTS_DIR


def write_git_objects(contents: bytes, obj_type: str, should_write: bool = True) -> str:
    # blob_object = b'blob' + b' ' + str(len(contents)).encode() + b'\x00' + contents
    blob_object = obj_type.encode("utf-8") + b' ' + str(len(contents)).encode() + b'\x00' + contents
    blob_object_hash = hashlib.sha1(blob_object).hexdigest()

    if should_write:
        # Determine the directory and file paths based on the SHA-1 hash
        folder_name = blob_object_hash[:2]
        file_name = blob_object_hash[2:]

        dir_path = os.path.join(OBJECTS_DIR, folder_name)
        file_path = os.path.join(dir_path, file_name)

        # Ensure the directory exists
        os.makedirs(dir_path, exist_ok=True)

        compressed_data = zlib.compress(blob_object)

        with open(file_path, 'wb') as f:
            f.write(compressed_data)

    return blob_object_hash

def decompress_git_objects(object_hash:bytes):
    folder_name = object_hash[:2]
    file_name = object_hash[2:]
    dir_path = OBJECTS_DIR / folder_name
    file_path = dir_path / file_name
    with open(file_path, "rb") as f:
        content_bytes = zlib.decompress(f.read())
        _, content_bytes = content_bytes.split(b"\0", maxsplit=1)
        return content_bytes
