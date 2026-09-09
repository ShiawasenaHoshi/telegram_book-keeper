#!/usr/bin/env python3
"""Build a .env file from a template and the process environment."""

from __future__ import annotations

import argparse
import os
import string
import sys
from collections.abc import Mapping
from pathlib import Path


class MissingValueError(RuntimeError):
    """Raised when the template needs a variable that is missing or empty."""


def render(template: str, values: Mapping[str, str]) -> str:
    tmpl = string.Template(template)
    errors: list[str] = []
    for name in tmpl.get_identifiers():
        value = values.get(name)
        if value is None or not str(value).strip():
            errors.append(
                f"Variable {name} is not set. Check vars and secrets "
                f"in the GitHub Environment for the selected environment."
            )
    if errors:
        raise MissingValueError("\n".join(errors))
    return tmpl.substitute(dict(values))


def render_file(template_path: Path, out_path: Path, values: Mapping[str, str]) -> None:
    rendered = render(template_path.read_text(encoding="utf-8"), values)
    descriptor = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(rendered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render .env from a template")
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        render_file(args.template, args.out, os.environ)
    except MissingValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
