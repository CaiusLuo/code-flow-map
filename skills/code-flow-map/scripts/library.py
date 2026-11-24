#!/usr/bin/env python3
"""List and remove Code Flow Map walkthroughs in ~/code-flow-map."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import secrets
import stat
import tempfile


METADATA = re.compile(rb'<script id="map-metadata" type="application/json">([^<]*)</script>')


def check_directory(folder):
    try:
        info = folder.lstat()
    except FileNotFoundError:
        return False
    if not stat.S_ISDIR(info.st_mode) or folder.resolve() != folder:
        raise ValueError(f"Expected a real directory at {folder}")
    return True


def library_folder():
    folder = Path.home().resolve() / "code-flow-map"
    check_directory(folder)
    return folder


def save_map(project, title, content):
    folder = library_folder()
    folder.mkdir(exist_ok=True, mode=0o700)
    check_directory(folder)
    stem = re.sub(r"[^\w-]+", "-", f"{project}-{title}").strip("-_").lower()[:64] or "flow"
    target = folder / f"{stem}-{secrets.token_hex(8)}.html"
    pending = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, delete=False)
    temporary = Path(pending.name)
    try:
        with pending:
            pending.write(content)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def map_file(folder, name):
    if (
        name.startswith(".") or not name.lower().endswith(".html")
        or any(char in name for char in "/\\:") or not name.isprintable()
    ):
        raise ValueError("Choose an HTML filename from the list.")
    path = folder / name
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"Expected a regular HTML file: {name}")
    return path, info


def read_metadata(path, expected):
    # Read the small metadata header without loading embedded source files.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    try:
        with os.fdopen(os.open(path, flags), "rb") as source:
            current = os.fstat(source.fileno())
            if not stat.S_ISREG(current.st_mode) or not os.path.samestat(current, expected):
                return {}
            marker = METADATA.search(source.read(8192))
        data = json.loads(marker[1]) if marker else {}
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def list_maps(folder):
    if not check_directory(folder):
        return []
    maps = []
    for entry in folder.iterdir():
        try:
            path, info = map_file(folder, entry.name)
        except (FileNotFoundError, ValueError):
            continue
        metadata = read_metadata(path, info)
        fields = {
            key: metadata[key] for key in ("title", "project", "repository", "revision")
            if isinstance(metadata.get(key), str) and metadata[key]
        }
        maps.append({
            "title": path.stem,
            **fields,
            "name": path.name,
            "path": str(path),
            "modified": datetime.fromtimestamp(info.st_mtime).astimezone().isoformat(timespec="seconds"),
        })
    return sorted(maps, key=lambda entry: (entry["modified"], entry["name"]), reverse=True)


def delete_map(folder, name):
    path, _ = map_file(folder, name)
    trash = folder / ".trash"
    trash.mkdir(exist_ok=True, mode=0o700)
    check_directory(trash)
    destination = Path(tempfile.mkdtemp(dir=trash))
    try:
        return path.rename(destination / path.name)
    except OSError:
        destination.rmdir()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List saved walkthroughs as JSON")
    delete = commands.add_parser("delete", help="Move one saved HTML file to .trash")
    delete.add_argument("name", help="Exact filename returned by list")
    args = parser.parse_args()

    try:
        folder = library_folder()
        if args.command == "list":
            result = {"folder": str(folder), "maps": list_maps(folder)}
        else:
            destination = delete_map(folder, args.name)
            result = {"name": args.name, "trash_path": str(destination)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Code Flow Map library: {error}\n")


if __name__ == "__main__":
    main()
