import hashlib
import sys
import os
import zlib


def write_sha_data(option: str, file_name: str, object_path) -> str:
    with open(file_name, "rb") as f:
        data = f.read()

    result = b'blob' + b' ' + str(len(data)).encode() + b'\x00' + data

    sha = hashlib.sha1(result).hexdigest()

    file_path = f"{object_path}/{sha[:2]}"
    # Extract the directory portion
    dir_path = os.path.dirname(file_path)

    # Create directories; won't raise an error if they already exist
    os.makedirs(dir_path, exist_ok=True)

    # Optional: Create the file after ensuring directories exist
    with open(sha[2:], 'wb') as f:
        f.write(result)

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

        sha1 = write_sha_data(option, file_name, object_path)

        return sha1
        # with open(f"{object_path}/{sha1[:2]}/{sha1[2:]}", "wb") as f:
        #     f.write(s)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
