import os
import time

from app.config import GIT_DIR, OBJECTS_DIR
from app.objects import write_git_objects, decompress_git_objects

def initialize():
    os.mkdir(GIT_DIR)
    os.mkdir(OBJECTS_DIR)
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")

def cat_file(blob_sha):
    content_bytes = decompress_git_objects(blob_sha)
    return content_bytes.decode(encoding="utf-8")

def write_sha_data(file_name):
    with open(file_name, "rb") as f:
        data = f.read()

    return write_git_objects(data, "blob")


def ls_tree(tree_hash):
    content_bytes = decompress_git_objects(tree_hash)
    while content_bytes:
        mode, binary_data = content_bytes.split(b"\x00", maxsplit=1)
        _, name = mode.split()
        binary_data = binary_data[20:]
        print(name.decode("utf-8"))


def commit(tree_sha, message_text, parent_sha):
    commit_content = b""

    commit_content += f"tree {tree_sha}\n".encode("utf-8")

    if parent_sha:
        commit_content += f"parent {parent_sha}\n".encode("utf-8")

    author = "Div D <test@test.com>"
    timestamp = time.strftime("%s %z", time.localtime())  # Unix timestamp + timezone

    commit_content += f"author {author} {timestamp}\n".encode("utf-8")
    commit_content += f"committer {author} {timestamp}\n".encode("utf-8")

    commit_content += b"\n"

    # Append commit message
    commit_content += message_text.encode("utf-8") + b"\n"

    header = f"commit {len(commit_content)}\0".encode("utf-8")
    full_commit_object = header + commit_content

    object_hash = write_git_objects(full_commit_object, "tree")

    return object_hash
