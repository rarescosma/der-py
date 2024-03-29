"""Do Obsidian stuff."""
import re
from functools import partial
from pathlib import Path
from typing import Callable, Iterable, List

import click

from ..fun import flatmap
from ..obsidian import Args, Line, Note, auto_alias, use_alias


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


@main.command("use-alias")
@click.option(
    "vault_dir",
    "-V",
    required=True,
    type=click.Path(dir_okay=True, file_okay=False, exists=True),
)
@click.option(
    "in_file",
    "-i",
    required=True,
    type=click.Path(dir_okay=False, file_okay=True, exists=True),
    multiple=True,
)
def do_use_alias(vault_dir: str, in_file: List[str]) -> None:
    """Replace plain links to aliased notes with aliased links."""
    replace_map = use_alias.vault_replace_map(Path(vault_dir))
    pattern = re.compile("|".join(replace_map.keys()))

    for f in in_file:
        args = Args(in_file=Path(f), out_file=Path(f))
        line_processor = partial(
            use_alias.process_line,
            re_pat=pattern,
            re_map=replace_map,
        )
        _process_file(args, line_processor)


def _process_file(
    args: Args,
    process_line: Callable[[Line], Iterable[str]],
) -> None:
    line_enum = enumerate(args.in_file.read_text().splitlines() or [""])
    lines = (Line(_, idx) for idx, _ in line_enum)
    args.out_file.write_text("\n".join(flatmap(process_line, lines)) + "\n")
