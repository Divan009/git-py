import os
import time

from app.config import GIT_DIR, OBJECTS_DIR
from app.objects import write_git_objects, decompress_git_objects
from app.utils import TreeEntry


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
    contents = decompress_git_objects(tree_hash)

    parsed_entries: list[TreeEntry] = []
    pos = 0

    # Iterate over the contents using a position pointer.
    while pos < len(contents):
        # Find the space that separates the file mode from the filename.
        space_index = contents.find(b" ", pos)
        if space_index == -1:
            break  # Malformed entry; no space found

        # The mode is from pos up to the space.
        mode = contents[pos:space_index].decode()

        # Find the null byte that terminates the filename.
        null_index = contents.find(b"\x00", space_index)
        if null_index == -1:
            break  # Malformed entry; no null terminator found

        # The filename is from after the space to the null byte.
        name = contents[space_index + 1:null_index].decode()

        # The SHA-1 hash is the 20 bytes immediately after the null byte.
        sha_start = null_index + 1
        sha_end = sha_start + 20
        sha_hash = contents[sha_start:sha_end].hex()
        # Append the parsed entry (convert SHA to hexadecimal representation)
        parsed_entries.append(TreeEntry(mode=mode, name=name, sha_hash=sha_hash))

        # Move the pointer to the start of the next entry
        pos = sha_end

    return parsed_entries


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

    object_hash = write_git_objects(commit_content, "commit")

    return object_hash
