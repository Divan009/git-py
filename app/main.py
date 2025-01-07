import sys
import os
import zlib

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

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
            with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as f:
                row = zlib.decompress(f.read())
                size, content = row.split(b"\0", maxsplit=1)
                print(content.decode(encoding="utf-8"), end="")
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
