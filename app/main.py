import sys
from argparse import ArgumentParser

from app.commands import initialize, cat_file, write_sha_data, ls_tree, commit
from app.utils import TreeClass


def main():

    command = sys.argv[1]
    match command:
        case "init":
            initialize()
            print("Initialized git directory")

        case "cat-file":
            parser = ArgumentParser(description="Reads a git object")
            parser.add_argument("object_hash")
            parser.add_argument(
                "--content",
                "-p",
                action="store_true",
                help="The content of the git object should be given",
            )

            args = parser.parse_args(sys.argv[2:])
            object_hash = args.object_hash

            contents = cat_file(object_hash)
            sys.stdout.write(contents)


        case "hash-object":
            parser = ArgumentParser(
                description="Computes the SHA hash of a git object. Optionally writes the object."
            )
            parser.add_argument("file_name")
            parser.add_argument(
                "--write",
                "-w",
                action="store_true",
                help="Specifies that the git object should be written to .git/objects",
            )
            args = parser.parse_args(sys.argv[2:])
            file_name = args.file_name

            object_hash = write_sha_data(file_name)
            print(object_hash)

            # sys.stdout.write(object_hash)

        case "ls-tree":
            parser = ArgumentParser(description="Show all the files in the repository like tree")
            parser.add_argument("tree_hash")
            parser.add_argument(
                "--name-only",
                action="store_true",
                help="Specifies the name of those files",
            )

            args = parser.parse_args(sys.argv[2:])
            tree_hash = args.tree_hash

            entries = ls_tree(tree_hash)

            if args.name_only:
                for entry in sorted(entries, key=lambda x: x.name):
                    print(entry.name)

        case "write-tree":
            tree_object = TreeClass()
            print(tree_object.write_tree(path="."))

        case "commit-tree":
            parser = ArgumentParser(description="Commit all the files in the repository")
            parser.add_argument("tree_sha")
            parser.add_argument(
                "-p",
                "--parent",
                help="Can specify the parent commit of the tree",
            )
            parser.add_argument(
                "-m",
                "--message",
                help="Can specify the commit message"
            )
            args = parser.parse_args(sys.argv[2:])
            tree_hash = args.tree_sha
            parent = args.parent
            message = args.message
            print(commit(tree_sha=tree_hash, message_text=message, parent_sha=parent))

        case "clone":
            parser = ArgumentParser(description="Clones a git repository")
            parser.add_argument("url")
            parser.add_argument("destination")
            args = parser.parse_args(sys.argv[2:])
            url = args.url
            clone_dir = args.destination
            pass
        case _:
            print(sys.exc_info()[0])
            raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()