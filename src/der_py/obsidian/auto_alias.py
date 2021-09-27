"""Infer an alias from the filename and write it as YAML front matter."""
from typing import Iterable, List

from . import Args, Line


def process_line(line: Line, aliases: List[str]) -> Iterable[str]:
    """Yield frontmatter + the rest of the file unchanged."""
    aliases_line = f"aliases: [{', '.join(map(_wrap_alias, aliases))}]"
    if line.no == 0:
        if line.text.startswith("---"):  # has frontmatter already
            yield line.text
            yield aliases_line
        else:  # no frontmatter, yield it all
            yield from ["---", aliases_line, "---"]
            yield line.text
    else:
        yield line.text


def get_aliases(args: Args) -> List[str]:
    """Return a list of file aliases."""
    alias = args.in_file.with_suffix("").name
    return (
        sorted({alias.lower(), alias})
        if args.extras.get("lower", False)
        else [alias]
    )


def _wrap_alias(alias: str) -> str:
    return f'"{alias}"'
