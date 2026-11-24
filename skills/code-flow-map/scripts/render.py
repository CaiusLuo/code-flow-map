#!/usr/bin/env python3
"""Generate a standalone flow walkthrough from a manifest and source snapshot."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import urlopen


TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "viewer.html"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, where):
    require(isinstance(value, str) and value.strip(), f"{where} needs text")
    return value


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}, timeout=30,
    ).stdout.decode("utf-8")


def github_repository(value):
    if "://" not in value:
        return None
    url = urlsplit(value)
    repository = url.path.strip("/").removesuffix(".git")
    require(
        url.scheme == "https" and url.netloc.lower() == "github.com" and not (url.query or url.fragment)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repository)
        and repository.split("/")[1] not in (".", ".."),
        "Use a local directory or a public GitHub repository URL such as https://github.com/owner/repo",
    )
    return repository


def github_commit(repository, ref):
    if ref and re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        return ref.lower()
    if ref is None or ref == "HEAD":
        names = ["HEAD"]
    elif ref.startswith("refs/tags/"):
        names = [ref + "^{}", ref]
    elif ref.startswith("refs/"):
        names = [ref]
    else:
        names = [f"refs/heads/{ref}", f"refs/tags/{ref}^{{}}", f"refs/tags/{ref}"]

    rows = git(Path.cwd(), "ls-remote", "--", f"https://github.com/{repository}.git", *names)
    remote_refs = {name: sha for sha, name in (line.split("\t", 1) for line in rows.splitlines())}
    revision = next((remote_refs[name] for name in names if name in remote_refs), "")
    require(re.fullmatch(r"[0-9a-f]{40}", revision), f"GitHub ref not found in {repository}: {ref or 'HEAD'}")
    return revision


def read_source(repo, revision, name):
    path = PurePosixPath(name)
    require(
        not path.is_absolute() and path.parts and ".." not in path.parts
        and "\\" not in name and name == path.as_posix(),
        f"Expected a repository-relative file path, got {name!r}",
    )
    if isinstance(repo, str):
        url = f"https://raw.githubusercontent.com/{repo}/{revision}/{quote(name)}"
        try:
            with urlopen(url, timeout=15) as response:
                return response.read().decode("utf-8")
        except HTTPError as error:
            raise ValueError(f"GitHub returned HTTP {error.code} for {repo}/{name} at {revision}") from error
    if revision:
        return git(repo, "cat-file", "blob", revision + ":" + name)
    source = (repo / name).resolve()
    require(source.is_relative_to(repo), f"Source file leaves the repository: {name}")
    return source.read_text(encoding="utf-8")


def place_nodes(nodes, paths):
    spine = paths[0]["steps"]
    require(len(spine) == len(set(spine)), "The first path must visit each main node once")
    positions = {name: (row, 1) for row, name in enumerate(spine, start=1)}
    links = dict.fromkeys(
        (origin, target)
        for path in paths
        for origin, target in zip(path["steps"], path["steps"][1:])
    )
    side_rows = set()
    for origin, destination in links:
        require(origin != destination, f"{origin}: add a distinct node to show this loop")
        if destination in spine:
            continue
        require(origin in spine, f"{destination}: a side node must follow a main node")
        row = positions[origin][0]
        if destination in positions:
            require(positions[destination][0] == row, f"{destination}: conflicting side placement")
        else:
            require(row not in side_rows, f"{origin}: only one side node fits beside a main node")
            positions[destination] = (row, 2)
            side_rows.add(row)

    require(positions.keys() == nodes.keys(), "Every node must appear in a path")
    edges = []
    for origin, destination in links:
        row, column = positions[origin]
        next_row, next_column = positions[destination]
        if next_column == 2:
            kind = "side"
        elif column == 2:
            kind = "retry" if next_row <= row else "tool-join"
        elif next_row < row:
            kind = "loop"
        else:
            kind = "down" if next_row == row + 1 else "skip"
        edges.append({"from": origin, "to": destination, "kind": kind})

    for name, (row, column) in positions.items():
        nodes[name].update(row=row, column=column, kind="branch" if column == 2 else "action")
    return sorted(nodes.values(), key=lambda node: (node["row"], node["column"])), edges


def load_snapshot(manifest, repo, revision, output):
    nodes = {}
    files = {}
    occupied = {}
    for node in manifest["nodes"]:
        name = text(node["id"], "Node ID")
        require(re.fullmatch("[a-z][a-z0-9-]*", name) and name not in nodes, f"Invalid or duplicate node ID: {name}")
        fields = {key: text(node[key], f"{name}.{key}") for key in ("title", "symbol", "description")}
        refs = []
        for ref in node["refs"]:
            filename = text(ref["file"], f"{name} source file")
            if filename not in files:
                if isinstance(repo, Path):
                    require(output != (repo / filename).resolve(), f"Output would overwrite {filename}")
                source = read_source(repo, revision, filename)
                require("\x00" not in source, f"{filename} is not a text source file")
                lines = source.replace("\r\n", "\n").replace("\r", "\n").removesuffix("\n").split("\n")
                files[filename] = {"path": filename, "lines": lines}
                occupied[filename] = set()
            start, end = ref["lines"]
            require(
                type(start) is int and type(end) is int and 1 <= start <= end <= len(files[filename]["lines"]),
                f"{name}: line range outside {filename}: {start}–{end}",
            )
            mapped = set(range(start, end + 1))
            require(not mapped & occupied[filename], f"{name}: overlapping reference in {filename}: {start}–{end}")
            occupied[filename].update(mapped)
            refs.append({"file": filename, "start": start, "end": end, "label": text(ref["label"], f"{name} source label")})
        require(refs, f"{name} needs at least one source reference")
        nodes[name] = {"id": name, **fields, "refs": refs}

    paths = []
    for path in manifest["paths"]:
        label = text(path["name"], "Path name")
        steps = path["steps"]
        require(isinstance(steps, list) and steps and all(step in nodes for step in steps), f"{label}: path contains no steps or an unknown node")
        paths.append({"name": label, "steps": steps})
    require(paths, "Add at least one path")

    rendered_nodes, edges = place_nodes(nodes, paths)
    language = manifest.get("language", "en")
    require(language in ("en", "zh"), "Language must be en or zh")
    return {
        "project": text(manifest["project"], "Project"), "title": text(manifest["title"], "Title"),
        "language": language, "revision": revision, "files": files,
        "repository": repo if isinstance(repo, str) else None,
        "nodes": rendered_nodes, "routes": paths, "edges": edges,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Source directory or public GitHub repository URL")
    parser.add_argument("--ref", help="Branch, tag, or commit (GitHub defaults to HEAD)")
    parser.add_argument("--manifest", type=Path, required=True, help="Flow manifest JSON")
    parser.add_argument("--out", type=Path, required=True, help="Standalone HTML file")
    args = parser.parse_args()

    try:
        output = args.out.resolve()
        require(output.suffix.lower() == ".html", "Output must have an .html extension")
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        repository = github_repository(args.repo)
        if repository:
            repo = repository
            revision = github_commit(repository, args.ref)
        else:
            repo = Path(args.repo).resolve(strict=True)
            revision = git(repo, "rev-parse", "--verify", "--end-of-options", args.ref + "^{commit}").strip() if args.ref else None
        snapshot = load_snapshot(manifest, repo, revision, output)
        payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        output.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__SNAPSHOT__", payload, 1), encoding="utf-8")
    except subprocess.CalledProcessError as error:
        parser.exit(2, error.stderr.decode("utf-8", errors="replace"))
    except (KeyError, TypeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f"Could not render flow: {error}\n")

    print(f"{output} ({len(snapshot['nodes'])} nodes, {len(snapshot['files'])} files)")


if __name__ == "__main__":
    main()
