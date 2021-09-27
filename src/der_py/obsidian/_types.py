"""Obsidian types: notes and such."""
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, NamedTuple

import yaml


@dataclass(frozen=True)
class Args:
    """Arguments model."""

    in_file: Path
    out_file: Path
    extras: Dict[str, Any] = field(default_factory=dict)


class Line(NamedTuple):
    """Line struct."""

    text: str
    no: int


Frontmatter = Dict[str, str]


@dataclass(frozen=True)
class Note:
    """Note model."""

    path: Path

    def rel_name(self, vault_dir: Path) -> str:
        """Name of the note relative to the vault root."""
        return f"{self.path.relative_to(vault_dir).with_suffix('')}"

    @cached_property
    def frontmatter(self) -> Frontmatter:
        """Parse the YAML frontmatter."""
        lines = self.path.read_text().splitlines()
        if not lines:
            return {}

        l_iter = iter(lines)
        if next(l_iter) == "---":
            frontmatter = ""
            while (l := next(l_iter)) != "---":
                frontmatter += l
                frontmatter += "\n"
            with suppress(yaml.YAMLError):
                return yaml.safe_load(frontmatter)

        return {}
