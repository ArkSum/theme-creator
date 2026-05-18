from pathlib import Path


def create_lua_groups(highlights_file: Path, theme: str,
                      colors: dict[str, list[str]]) -> None:
    contents = ""

    for group, colorset in colors.items():
        pass

    with open(highlights_file, 'w') as file:
        file.write(contents)
    return
