import hashlib
import sys
import os
import time
import zlib


def commit(tree_sha, message_text, parent_sha):
    commit_content = b""

    commit_content += f"tree {tree_sha}\n".encode("utf-8")

    if parent_sha:
        commit_content += f"parent {parent_sha}\n".encode("utf-8")

    author = "Div Shiv <test@test.com>"
    timestamp = time.strftime("%s %z", time.localtime())  # Unix timestamp + timezone

    commit_content += f"author {author} {timestamp}\n".encode("utf-8")
    commit_content += f"committer {author} {timestamp}\n".encode("utf-8")

    commit_content += b"\n"

    # Append commit message
    commit_content += message_text.encode("utf-8") + b"\n"

    header = f"commit {len(commit_content)}\0".encode("utf-8")
    full_commit_object = header + commit_content

    # Compute SHA-1 hash for the blob object.
    blob_sha = hashlib.sha1(full_commit_object).hexdigest()
    # Compress the blob object.
    compressed_blob = zlib.compress(full_commit_object)

    folder_name = blob_sha[:2]
    file_name = blob_sha[2:]

    full_path = os.path.join(".git", "objects", folder_name)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    object_path = os.path.join(full_path, file_name)
    with open(object_path, 'wb') as f:
        f.write(compressed_blob)

    return blob_sha


def write_tree(path="."):
    """
     :return: sha
    """

    result = []
    with os.scandir(path) as entries:
        for entry in entries:
            full_path = os.path.join(path, entry.name)

            #  create a tree object and record hash
            if entry.is_dir():
                if entry.name == ".git":
                    continue
                tree_sha = write_tree(full_path)
                # Convert the hex digest to raw 20-byte binary value
                tree_sha_bin = bytes.fromhex(tree_sha)
                # Append a tree entry with mode "40000" for directories
                result.append((entry.name, "40000", tree_sha_bin))
            # entry is a file, create a blob object and record its SHA hash
            elif entry.is_file():
                # Create a blob for the file
                hash = write_blob(full_path)
                blob_sha_bin = bytes.fromhex(hash)
                # Append a blob entry with mode "100644" (regular file)
                result.append((entry.name, "100644", blob_sha_bin))

        result.sort(key=lambda e: e[0])
        # Build the tree object content: for each entry, append
        # "<mode> <name>\0<20_byte_sha>"
        tree_content = b""
        for name, mode, sha in result:
            entry = f"{mode} {name}".encode("utf-8") + b"\x00" + sha
            tree_content += entry

        header = f"tree {len(tree_content)}\0".encode("utf-8")
        full_tree_object = header + tree_content

        # Compute the SHA-1 hash for the tree object
        full_tree_object_hash = hashlib.sha1(full_tree_object).hexdigest()

        full_tree_object_compress = zlib.compress(full_tree_object)

        # Determine the storage location for the tree object
        object_dir = os.path.join(".git", "objects", full_tree_object_hash[:2])
        if not os.path.exists(object_dir):
            os.makedirs(object_dir)
        object_path = os.path.join(object_dir, full_tree_object_hash[2:])

        # Write the object if it doesn't exist already
        if not os.path.exists(object_path):
            with open(object_path, "wb") as f:
                f.write(full_tree_object_compress)

    return full_tree_object_hash


def write_blob(file_path: str) -> str:
    """
    Reads the file at 'file_path', creates a blob object,
    writes it to .git/objects, and returns its SHA-1 hash.
    """
    with open(file_path, "rb") as f:
        data = f.read()

    # Build the blob object: header "blob <size>\0" + data.
    header = f"blob {len(data)}\0".encode("utf-8")
    blob_object = header + data

    # Compute SHA-1 hash for the blob object.
    blob_sha = hashlib.sha1(blob_object).hexdigest()

    # Compress the blob object.
    compressed_blob = zlib.compress(blob_object)

    # Determine the storage location under .git/objects
    object_dir = os.path.join(".git", "objects", blob_sha[:2])
    if not os.path.exists(object_dir):
        os.makedirs(object_dir)
    object_path = os.path.join(object_dir, blob_sha[2:])

    # Write the blob object if it doesn't already exist.
    if not os.path.exists(object_path):
        with open(object_path, "wb") as f:
            f.write(compressed_blob)

    return blob_sha

def write_sha_data(file_name: str, object_path) -> str:
    with open(file_name, "rb") as f:
        data = f.read()

    result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data

    sha = hashlib.sha1(result).hexdigest()

    # Determine the directory and file paths based on the SHA-1 hash
    dir_path = os.path.join(object_path, sha[:2])
    file_path = os.path.join(dir_path, sha[2:])

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    compressed_data = zlib.compress(result)

    with open(file_path, 'wb') as f:
        f.write(compressed_data)

    return sha


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    object_path = ".git/objects"

    # Uncomment this block to pass the first stage
    #
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        if len(sys.argv) < 4:
            print("Usage: script.py cat-file -p <blob_sha>")
            sys.exit(1)

        option = sys.argv[2]
        blob_sha = sys.argv[3]

        if option == "-p":
            with open(f"{object_path}/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as f:
                row = zlib.decompress(f.read())
                size, content = row.split(b"\0", maxsplit=1)
                print(content.decode(encoding="utf-8"), end="")

    elif command == "hash-object":
        if len(sys.argv) < 4:
            print("Usage: script.py hash-object -w test.txt")
            sys.exit(1)

        option = sys.argv[2]
        file_name = sys.argv[3]

        sha1 = write_sha_data(file_name, object_path)

        print(sha1)

    elif command == "ls-tree":
        option = sys.argv[2]
        sha_hash = sys.argv[3]

        if option == "--name-only":
            with open(f".git/objects/{sha_hash[:2]}/{sha_hash[2:]}", "rb") as f:
                data = zlib.decompress(f.read())
                _, binary_data = data.split(b"\x00", maxsplit=1)
                while binary_data:
                    mode, binary_data = binary_data.split(b"\x00", maxsplit=1)
                    _, name = mode.split()
                    binary_data = binary_data[20:]
                    print(name.decode("utf-8"))

    elif command == "write-tree":
        print(write_tree())

    elif command == "commit-tree":
        tree_sha, parent_option, commit_sha, msg_option, msg = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
        print(commit(tree_sha=tree_sha, message_text=msg, parent_sha=commit_sha))

    elif command == "clone":
        pass
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
