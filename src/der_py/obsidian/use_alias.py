"""
Scans vault for all notes with aliases and populates a map.

Then scans the input file for lines containing links to notes
in the map and replaces them with aliased links:

[[an/aliased/note]] -> [[an/aliased/note|the_alias]]
"""
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Union, cast

from . import Line, Note
from ..fun import flatmap

AbsName = str
Alias = str
PageLink = str
AliasedLink = str

AliasMap = Dict[Alias, AbsName]
ReplaceMap = Dict[PageLink, AliasedLink]


def vault_replace_map(vault_dir: Path) -> ReplaceMap:
    """Compute the replace map for the given vault dir."""
    return _replace_map(_alias_map(vault_dir))


def _alias_map(from_dir: Path) -> AliasMap:
    notes = (Note(path=_) for _ in from_dir.rglob("**/*.md"))
    return {
        alias: note.rel_name(from_dir)
        for note in notes
        for alias in _all_aliases(note)
    }


def _all_aliases(note: Note) -> list[str]:
    return sorted(
        set(
            flatmap(
                _pack_alias,
                [
                    note.frontmatter.get("alias", []),
                    note.frontmatter.get("aliases", []),
                ],
            )
        )
    )


def _pack_alias(alias: Any) -> list[str]:
    if type(alias) == str:
        return [cast(str, alias)]
    elif type(alias) == list:
        return cast(list[str], alias)
    return []


def _replace_map(alias_map: AliasMap) -> ReplaceMap:
    return {
        re.escape(f"[[{abs_name}]]"): f"[[{abs_name}|{alias}]]"
        for alias, abs_name in alias_map.items()
        if alias != abs_name
    }


def process_line(
    line: Line, re_pat: re.Pattern, re_map: Dict[str, str]
) -> Iterable[str]:
    """Replace links according to map and pattern."""
    yield re_pat.sub(lambda m: re_map[re.escape(m.group(0))], line.text)
