"""Do Obsidian stuff."""
from functools import partial
from pathlib import Path
from typing import Callable, Iterable, List

import click

from ..fun import flatmap
from ..obsidian import Args, Line, Note, auto_alias


@click.group()
def main() -> None:
    """Process a list of Obsidian note files."""


@main.command("auto-alias")
@click.option(
    "in_file",
    "-i",
    required=True,
    type=click.Path(dir_okay=False, file_okay=True, exists=True),
    multiple=True,
)
@click.option("lower", "--lower", is_flag=True, required=False, default=False)
def do_auto_alias(in_file: List[str], lower: bool) -> None:
    """Infer an alias from the filename and write it as YAML front matter."""
    for f in in_file:
        args = Args(
            in_file=Path(f),
            out_file=Path(f),
            extras={"lower": lower},
        )
        note = Note(args.in_file)
        if set(note.frontmatter.keys()) & {"alias", "aliases"}:
            continue
        line_processor = partial(
            auto_alias.process_line, aliases=auto_alias.get_aliases(args)
        )
        _process_file(args, line_processor)


def _process_file(
    args: Args,
    process_line: Callable[[Line], Iterable[str]],
) -> None:
    line_enum = enumerate(args.in_file.read_text().splitlines() or [""])
    lines = (Line(_, idx) for idx, _ in line_enum)
    args.out_file.write_text("\n".join(flatmap(process_line, lines)) + "\n")
