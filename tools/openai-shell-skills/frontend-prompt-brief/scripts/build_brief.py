#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from string import Template


REQUIRED_KEYS = [
    "surface_type",
    "product",
    "audience",
    "goal",
    "primary_cta",
    "style",
    "palette",
    "mood",
    "implementation_target",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic frontend brief Markdown artifact from JSON input."
        ),
    )
    parser.add_argument("--input", required=True, help="Path to the input JSON file.")
    parser.add_argument(
        "--output", required=True, help="Path to the output Markdown file."
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_keys(data: dict) -> None:
    missing = [key for key in REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise SystemExit(f"Missing required keys: {', '.join(missing)}")


def format_list(value, empty_label: str) -> str:
    if not value:
        return f"- {empty_label}"
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return f"- {value}"


def render(template_path: Path, data: dict) -> str:
    template = Template(template_path.read_text(encoding="utf-8"))
    substitutions = {
        "surface_type": data["surface_type"],
        "product": data["product"],
        "brand": data.get("brand", "TBD"),
        "audience": data["audience"],
        "goal": data["goal"],
        "primary_cta": data["primary_cta"],
        "implementation_target": data["implementation_target"],
        "style": data["style"],
        "palette": data["palette"],
        "mood": data["mood"],
        "sections": format_list(
            data.get("sections"), "Define 3-5 sections before implementation."
        ),
        "constraints": format_list(
            data.get("constraints"), "Add product and layout constraints."
        ),
        "references": format_list(data.get("references"), "No references provided."),
    }
    return template.substitute(substitutions)


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent
    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = skill_root / "assets" / "brief-template.md"

    data = load_json(input_path)
    require_keys(data)
    rendered = render(template_path, data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote frontend brief to {output_path}")


if __name__ == "__main__":
    main()
