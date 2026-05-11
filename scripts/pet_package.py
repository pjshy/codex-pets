#!/usr/bin/env python3
"""Build or install a Codex custom pet package from local assets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ATLAS_COLS = 8
ATLAS_ROWS = 9
CELL_W = 192
CELL_H = 208
ATLAS_W = ATLAS_COLS * CELL_W
ATLAS_H = ATLAS_ROWS * CELL_H
BASELINE = 8
GLOBAL_X_BIAS = -24
GLOBAL_Y_BIAS = 18
DEFAULT_OUTPUT_DIR = "dist/codex-pets-package/codex-pets"


@dataclass(frozen=True)
class FrameSpec:
    source: str
    x_shift: int = 0
    y_shift: int = 0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    mirror: bool = False
    brightness: float = 1.0
    contrast: float = 1.0


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or "~/.codex").expanduser().resolve()


def trim_to_alpha(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def load_source(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    image = trim_to_alpha(image)
    return ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)


def transform_frame(base: Image.Image, spec: FrameSpec) -> Image.Image:
    frame = base.copy()

    if spec.mirror:
        frame = ImageOps.mirror(frame)

    if spec.scale_x != 1.0 or spec.scale_y != 1.0:
        scaled_w = max(1, round(frame.width * spec.scale_x))
        scaled_h = max(1, round(frame.height * spec.scale_y))
        frame = frame.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    if spec.rotation:
        frame = frame.rotate(spec.rotation, expand=True, resample=Image.Resampling.BICUBIC)

    if spec.brightness != 1.0:
        frame = ImageEnhance.Brightness(frame).enhance(spec.brightness)

    if spec.contrast != 1.0:
        frame = ImageEnhance.Contrast(frame).enhance(spec.contrast)

    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - frame.width) // 2 + GLOBAL_X_BIAS + spec.x_shift
    y = CELL_H - frame.height - BASELINE + GLOBAL_Y_BIAS + spec.y_shift
    cell.paste(frame, (x, y), frame)
    return cell


def write_manifest(path: Path, pet_id: str, display_name: str, description: str) -> None:
    manifest = {
        "id": pet_id,
        "displayName": display_name,
        "description": description,
        "spritesheetPath": "spritesheet.webp",
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_package(repo_root: Path, pet_id: str, display_name: str, description: str, output_dir: Path) -> dict[str, str | bool]:
    output_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        "idle": load_source(repo_root / "assets/dex-idle.png", (CELL_W - 56, CELL_H - 42)),
        "interactive": load_source(repo_root / "assets/dex-interactive.png", (CELL_W - 50, CELL_H - 36)),
        "focus": load_source(repo_root / "assets/dex-focus.png", (CELL_W - 46, CELL_H - 30)),
    }

    rows: list[list[FrameSpec]] = [
        [
            FrameSpec("idle", y_shift=0, scale_y=0.985),
            FrameSpec("idle", y_shift=-3, scale_y=1.0),
            FrameSpec("idle", y_shift=-5, scale_y=1.015),
            FrameSpec("idle", y_shift=-3, scale_y=1.005),
            FrameSpec("idle", y_shift=-1, scale_y=0.995),
            FrameSpec("idle", y_shift=0, scale_y=0.985),
        ],
        [
            FrameSpec("interactive", x_shift=-12, y_shift=2, rotation=-4, scale_x=0.985, scale_y=0.99),
            FrameSpec("interactive", x_shift=-8, y_shift=0, rotation=-2, scale_x=0.995, scale_y=1.0),
            FrameSpec("interactive", x_shift=-3, y_shift=-2, rotation=0, scale_x=1.005, scale_y=1.01),
            FrameSpec("interactive", x_shift=2, y_shift=-3, rotation=2, scale_x=1.01, scale_y=1.015),
            FrameSpec("interactive", x_shift=7, y_shift=-2, rotation=3, scale_x=1.005, scale_y=1.01),
            FrameSpec("interactive", x_shift=11, y_shift=0, rotation=1, scale_x=0.995, scale_y=1.0),
            FrameSpec("interactive", x_shift=14, y_shift=2, rotation=-1, scale_x=0.985, scale_y=0.99),
            FrameSpec("interactive", x_shift=9, y_shift=1, rotation=-2, scale_x=0.99, scale_y=0.995),
        ],
        [
            FrameSpec("interactive", x_shift=12, y_shift=2, rotation=4, scale_x=0.985, scale_y=0.99, mirror=True),
            FrameSpec("interactive", x_shift=8, y_shift=0, rotation=2, scale_x=0.995, scale_y=1.0, mirror=True),
            FrameSpec("interactive", x_shift=3, y_shift=-2, rotation=0, scale_x=1.005, scale_y=1.01, mirror=True),
            FrameSpec("interactive", x_shift=-2, y_shift=-3, rotation=-2, scale_x=1.01, scale_y=1.015, mirror=True),
            FrameSpec("interactive", x_shift=-7, y_shift=-2, rotation=-3, scale_x=1.005, scale_y=1.01, mirror=True),
            FrameSpec("interactive", x_shift=-11, y_shift=0, rotation=-1, scale_x=0.995, scale_y=1.0, mirror=True),
            FrameSpec("interactive", x_shift=-14, y_shift=2, rotation=1, scale_x=0.985, scale_y=0.99, mirror=True),
            FrameSpec("interactive", x_shift=-9, y_shift=1, rotation=2, scale_x=0.99, scale_y=0.995, mirror=True),
        ],
        [
            FrameSpec("interactive", x_shift=-2, y_shift=0, rotation=-2, scale_y=0.995),
            FrameSpec("interactive", x_shift=2, y_shift=-2, rotation=4, scale_y=1.01),
            FrameSpec("interactive", x_shift=5, y_shift=-3, rotation=8, scale_y=1.015),
            FrameSpec("interactive", x_shift=1, y_shift=-1, rotation=1, scale_y=1.0),
        ],
        [
            FrameSpec("focus", y_shift=5, scale_y=0.96, scale_x=1.02),
            FrameSpec("focus", y_shift=0, scale_y=1.0, scale_x=1.0),
            FrameSpec("focus", y_shift=-10, scale_y=1.05, scale_x=0.98),
            FrameSpec("focus", y_shift=-3, scale_y=1.015, scale_x=0.995),
            FrameSpec("focus", y_shift=3, scale_y=0.985, scale_x=1.01),
        ],
        [
            FrameSpec("idle", x_shift=0, y_shift=1, rotation=0, brightness=0.98),
            FrameSpec("idle", x_shift=-3, y_shift=3, rotation=-4, brightness=0.95, contrast=0.98),
            FrameSpec("idle", x_shift=-5, y_shift=6, rotation=-7, brightness=0.92, contrast=0.96),
            FrameSpec("idle", x_shift=-2, y_shift=8, rotation=-3, brightness=0.9, contrast=0.95),
            FrameSpec("idle", x_shift=2, y_shift=8, rotation=3, brightness=0.9, contrast=0.95),
            FrameSpec("idle", x_shift=5, y_shift=6, rotation=7, brightness=0.92, contrast=0.96),
            FrameSpec("idle", x_shift=3, y_shift=3, rotation=4, brightness=0.95, contrast=0.98),
            FrameSpec("idle", x_shift=0, y_shift=1, rotation=0, brightness=0.98),
        ],
        [
            FrameSpec("idle", x_shift=-4, y_shift=1, rotation=-5, scale_y=0.99),
            FrameSpec("idle", x_shift=0, y_shift=-1, rotation=0, scale_y=1.0),
            FrameSpec("idle", x_shift=4, y_shift=1, rotation=5, scale_y=0.99),
            FrameSpec("idle", x_shift=2, y_shift=2, rotation=3, scale_y=0.985),
            FrameSpec("idle", x_shift=-2, y_shift=2, rotation=-3, scale_y=0.985),
            FrameSpec("idle", x_shift=0, y_shift=0, rotation=0, scale_y=1.0),
        ],
        [
            FrameSpec("focus", x_shift=-5, y_shift=2, rotation=-5, scale_x=0.995, scale_y=0.99),
            FrameSpec("focus", x_shift=-2, y_shift=-1, rotation=-2, scale_x=1.0, scale_y=1.0),
            FrameSpec("focus", x_shift=2, y_shift=-3, rotation=2, scale_x=1.01, scale_y=1.015),
            FrameSpec("focus", x_shift=5, y_shift=-1, rotation=5, scale_x=1.005, scale_y=1.0),
            FrameSpec("focus", x_shift=2, y_shift=2, rotation=2, scale_x=0.995, scale_y=0.99),
            FrameSpec("focus", x_shift=-2, y_shift=1, rotation=-2, scale_x=0.99, scale_y=0.985),
        ],
        [
            FrameSpec("focus", x_shift=-4, y_shift=2, rotation=-7, scale_x=0.985, scale_y=0.99, contrast=1.03),
            FrameSpec("focus", x_shift=-1, y_shift=-1, rotation=-3, scale_x=0.995, scale_y=1.0, contrast=1.05),
            FrameSpec("focus", x_shift=0, y_shift=-4, rotation=0, scale_x=1.01, scale_y=1.02, contrast=1.07),
            FrameSpec("focus", x_shift=2, y_shift=-3, rotation=4, scale_x=1.005, scale_y=1.015, contrast=1.08),
            FrameSpec("focus", x_shift=4, y_shift=0, rotation=7, scale_x=0.995, scale_y=1.0, contrast=1.06),
            FrameSpec("focus", x_shift=1, y_shift=2, rotation=2, scale_x=0.985, scale_y=0.99, contrast=1.04),
        ],
    ]

    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    for row_index, row in enumerate(rows):
        for col_index, frame_spec in enumerate(row):
            frame = transform_frame(sources[frame_spec.source], frame_spec)
            atlas.paste(frame, (col_index * CELL_W, row_index * CELL_H), frame)

    atlas_path = output_dir / "spritesheet.webp"
    atlas.save(atlas_path, format="WEBP", lossless=True, quality=100, method=6)

    manifest_path = output_dir / "pet.json"
    write_manifest(manifest_path, pet_id, display_name, description)

    return {
        "ok": True,
        "output_dir": str(output_dir),
        "manifest": str(manifest_path),
        "spritesheet": str(atlas_path),
    }


def install_package(package_dir: Path, pet_id: str, codex_home: Path, force: bool) -> dict[str, str | bool]:
    manifest = package_dir / "pet.json"
    spritesheet = package_dir / "spritesheet.webp"
    if not manifest.exists() or not spritesheet.exists():
        raise SystemExit(f"package missing under {package_dir}; build it first")

    install_dir = codex_home / "pets" / pet_id
    install_dir.mkdir(parents=True, exist_ok=True)

    if not force:
        existing = [p for p in [install_dir / "pet.json", install_dir / "spritesheet.webp"] if p.exists()]
        if existing:
            raise SystemExit(f"{install_dir} already contains pet files; pass --force to overwrite")

    shutil.copy2(manifest, install_dir / "pet.json")
    shutil.copy2(spritesheet, install_dir / "spritesheet.webp")

    return {
        "ok": True,
        "install_dir": str(install_dir),
        "manifest": str(install_dir / "pet.json"),
        "spritesheet": str(install_dir / "spritesheet.webp"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "install", "reinstall"], nargs="?", default="reinstall")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--pet-id", default="codex-pets")
    parser.add_argument("--display-name", default="Codex Pets")
    parser.add_argument("--description", default="A Codex custom pet package generated from the codex-pets project assets.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--codex-home", default=str(default_codex_home()))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    codex_home = Path(args.codex_home).expanduser().resolve()

    if args.action == "build":
        print(json.dumps(build_package(repo_root, args.pet_id, args.display_name, args.description, output_dir), indent=2))
        return

    if args.action == "install":
        print(json.dumps(install_package(output_dir, args.pet_id, codex_home, args.force), indent=2))
        return

    build_result = build_package(repo_root, args.pet_id, args.display_name, args.description, output_dir)
    install_result = install_package(output_dir, args.pet_id, codex_home, True)
    print(json.dumps({"build": build_result, "install": install_result}, indent=2))


if __name__ == "__main__":
    main()
