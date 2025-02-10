import hashlib
import sys
import os
import zlib


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


def write_tree()


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
        tree_sha = sys.argv[3]

        if option == "--name-only":
            with open(f".git/objects/{hash[:2]}/{hash[2:]}", "rb") as f:
                data = zlib.decompress(f.read())
                _, binary = data.split(b"\x00", maxsplit=1)
                while binary:
                    mode, binary_data = binary.split(b"\x00", maxsplit=1)
                    _, name = mode.split()
                    binary_data = binary_data[20:]
                    print(name.decode("utf-8"))
    else:
        sys.exit(1)



    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
