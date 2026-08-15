#!/usr/bin/env python3

"""Build the firmware matrix inside ZMK's official Docker image."""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


WORKSPACE = Path("/workspace")
SOURCE = Path("/source")
DIST = Path("/dist")
BUILD_ROOT = WORKSPACE / "build"


def run(command: list[str]) -> None:
    print("+ " + shlex.join(command), flush=True)
    subprocess.run(command, cwd=WORKSPACE, check=True)


def artifact_name(entry: dict[str, object]) -> str:
    explicit = entry.get("artifact-name")
    if explicit:
        return str(explicit)

    board = str(entry["board"]).replace("/", "_")
    shield = entry.get("shield")
    return f"{shield}-{board}-zmk" if shield else f"{board}-zmk"


def load_targets() -> list[dict[str, object]]:
    with (SOURCE / "build.yaml").open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)

    targets = document.get("include") if isinstance(document, dict) else None
    if not isinstance(targets, list) or not targets:
        raise SystemExit("error: build.yaml does not contain a non-empty 'include' list")

    for target in targets:
        if not isinstance(target, dict) or not target.get("board"):
            raise SystemExit("error: every build.yaml entry must contain a board")
    return targets


def select_targets(
    targets: list[dict[str, object]], selector: str | None
) -> list[dict[str, object]]:
    if selector is None:
        return targets

    selected = [target for target in targets if artifact_name(target) == selector]
    if selected:
        return selected

    available = "\n".join(f"  - {artifact_name(target)}" for target in targets)
    raise SystemExit(f"error: unknown target '{selector}'\nAvailable targets:\n{available}")


def prepare_workspace() -> None:
    if not (WORKSPACE / ".west" / "config").exists():
        run(["west", "init", "-l", "config"])
    else:
        run(["west", "config", "manifest.path", "config"])
        run(["west", "config", "manifest.file", "west.yml"])

    run(["west", "update", "--fetch-opt=--filter=tree:0"])
    run(["west", "zephyr-export"])


def clean_dist(targets: list[dict[str, object]], full_build: bool) -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if full_build:
        for path in DIST.iterdir():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
        return

    for target in targets:
        name = artifact_name(target)
        for suffix in ("uf2", "bin"):
            (DIST / f"{name}.{suffix}").unlink(missing_ok=True)


def build(target: dict[str, object]) -> Path:
    name = artifact_name(target)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    build_dir = BUILD_ROOT / safe_name

    command = [
        "west",
        "build",
        "--pristine=auto",
        "-s",
        str(WORKSPACE / "zmk" / "app"),
        "-d",
        str(build_dir),
        "-b",
        str(target["board"]),
    ]
    if target.get("snippet"):
        command.extend(["-S", str(target["snippet"])])

    command.extend(
        [
            "--",
            f"-DZMK_CONFIG={SOURCE / 'config'}",
            f"-DZMK_EXTRA_MODULES={SOURCE}",
        ]
    )
    if target.get("shield"):
        command.append(f"-DSHIELD={target['shield']}")
    if target.get("cmake-args"):
        command.extend(shlex.split(str(target["cmake-args"])))

    run(command)

    output_dir = build_dir / "zephyr"
    for suffix in ("uf2", "bin"):
        source_artifact = output_dir / f"zmk.{suffix}"
        if source_artifact.is_file():
            destination = DIST / f"{name}.{suffix}"
            temporary = DIST / f".{name}.{suffix}.tmp"
            shutil.copy2(source_artifact, temporary)
            temporary.replace(destination)
            return destination

    raise SystemExit(f"error: build succeeded but no UF2 or BIN was produced for {name}")


def set_host_ownership(paths: list[Path]) -> None:
    try:
        uid = int(os.environ["HOST_UID"])
        gid = int(os.environ["HOST_GID"])
    except (KeyError, ValueError):
        return

    for path in paths:
        try:
            os.chown(path, uid, gid)
        except PermissionError:
            pass


def main() -> None:
    if len(sys.argv) > 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} [artifact-name]")

    targets = load_targets()
    selector = sys.argv[1] if len(sys.argv) == 2 else None
    selected = select_targets(targets, selector)
    clean_dist(selected, full_build=selector is None)
    prepare_workspace()

    outputs = [build(target) for target in selected]
    set_host_ownership(outputs)

    print("\nFirmware artifacts:")
    for output in outputs:
        print(f"  {output}")


if __name__ == "__main__":
    main()
