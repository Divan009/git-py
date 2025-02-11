import hashlib
import os
from dataclasses import dataclass

from app.objects import write_git_objects


class GithubClone:
    def __init__(self, url, dir):
        self.url = url


    def clone(self):
        ...

@dataclass
class TreeEntry:
    mode: str
    name: str
    sha_hash: str

    def to_bytes(self) -> bytes:
        return (
            self.mode.encode()
            + b" "
            + self.name.encode()
            + b"\x00"
            + bytes.fromhex(self.sha_hash)
        )

class TreeClass:

    def _get_mode_for_entry(self, entry: os.DirEntry) -> str:
        if entry.is_dir():
            return "40000"
        if entry.is_symlink():
            return "120000"
        if entry.is_file():
            if os.access(entry.path, os.X_OK):
                return "100755"
            return "100644"
        raise Exception("Invalid entry")

    def _create_tree_structure(self, path: str | None = "."):
        result: list[TreeEntry] = []

        with os.scandir(path) as entries:
            for entry in entries:
                full_path = os.path.join(path, entry.name)

                #  create a tree object and record hash
                if entry.is_dir():
                    if entry.name == ".git":
                        continue
                    tree_sha = self.write_tree(full_path)
                    # Convert the hex digest to raw 20-byte binary value
                    # tree_sha_bin = bytes.fromhex(tree_sha)
                    # Append a tree entry with mode "40000" for directories
                    result.append(
                        TreeEntry(
                            mode=self._get_mode_for_entry(entry),
                            name=entry.name,
                            sha_hash=tree_sha,
                        )
                    )
                # entry is a file, create a blob object and record its SHA hash
                elif entry.is_file():
                    # Create a blob for the file
                    with open(full_path, "rb") as f:
                        data = f.read()

                    hash = write_git_objects(data, "blob")
                    # blob_sha_bin = bytes.fromhex(hash)
                    # Append a blob entry with mode "100644" (regular file)
                    result.append(
                        TreeEntry(
                            mode=self._get_mode_for_entry(entry),
                            name=entry.name,
                            sha_hash=hash,
                        )
                    )
        return result

    def _encode_tree(self, tree):
        contents = b"".join(
            [entry.to_bytes() for entry in sorted(tree, key=lambda entry: entry.name)]
        )
        blob_object = "tree".encode() + b" " + str(len(contents)).encode() + b"\x00" + contents
        object_hash = hashlib.sha1(blob_object).digest()
        return object_hash, contents

        # header = f"tree {len(tree_content)}\0".encode("utf-8")
        # full_tree_object = header + tree_content


    def write_tree(self, path: str | None = None) -> str:
        tree = self._create_tree_structure(path)
        _, contents = self._encode_tree(tree)
        object_hash = write_git_objects(contents, "tree")

        return object_hash

