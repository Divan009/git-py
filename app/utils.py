import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

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
        # Returns: b"<mode> <name>\0<20-byte sha>"
        return f"{self.mode} {self.name}\x00".encode("utf-8") + bytes.fromhex(self.sha_hash)


class Tree:
    def _get_mode_for_entry(self, entry: os.DirEntry) -> str:
        if entry.is_dir():
            return "40000"
        if entry.is_symlink():
            return "120000"
        if entry.is_file():
            return "100755" if os.access(entry.path, os.X_OK) else "100644"
        raise Exception("Invalid entry type encountered")

    def _create_tree_structure(self, path: str = ".") -> list[TreeEntry]:
        tree_entries: list[TreeEntry] = []
        path_obj = Path(path)

        # Using os.scandir for efficiency
        with os.scandir(path) as entries:
            for entry in entries:
                # Skip the .git directory
                if entry.name == ".git":
                    continue

                full_path = path_obj / entry.name

                if entry.is_dir():
                    # Recursively write the tree for subdirectories.
                    subtree_sha = self.write_tree(str(full_path))
                    tree_entries.append(
                        TreeEntry(
                            mode=self._get_mode_for_entry(entry),
                            name=entry.name,
                            sha_hash=subtree_sha,
                        )
                    )
                elif entry.is_file():
                    # Read file data and create a blob.
                    data = full_path.read_bytes()
                    blob_sha = write_git_objects(data, "blob")
                    tree_entries.append(
                        TreeEntry(
                            mode=self._get_mode_for_entry(entry),
                            name=entry.name,
                            sha_hash=blob_sha,
                        )
                    )
        return tree_entries

    def _encode_tree(self, tree_entries: list[TreeEntry]) -> bytes:
        # Sort entries by name for consistent ordering.
        contents = b"".join(entry.to_bytes() for entry in sorted(tree_entries, key=lambda e: e.name))
        header = f"tree {len(contents)}\0".encode("utf-8")
        return header + contents

    def write_tree(self, path: str = ".") -> str:
        tree_entries = self._create_tree_structure(path)
        tree_object = self._encode_tree(tree_entries)
        object_hash = write_git_objects(tree_object, "tree")
        return object_hash