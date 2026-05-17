from pathlib import Path


def create_lua_groups(highlights_file: Path, theme: str,
                      colors: dict[str, list[str]]) -> None:
    contents = f"""
local M = {{}}

function M.setup()
    vim.cmd("highlight clear")
    vim.cmd("syntax reset")

    vim.o.background = "dark"
    vim.g.colors_name = {theme}

    local set = vim.api.nvim_set_hl

"""

    theme_mappings = {
        "basic": {
            0: [  # Background, darkest
            ],
            1: [  # Background, dark
            ],
            2: [  # Foreground, medium
            ],
            3: [  # Foreground, light
            ],
            4: [  # Foreground, lightest
            ]
        },
        "highlight": {
            0: [  # Medium highlight
            ],
            1: [  # Bright highlight
            ],
            2: [  # Warning Color
            ],
            3: [  # Error Color
            ],
        },
        "git": {
            0: "Added",
            1: "Changed",
            2: "Removed",
            # Ignored
            3: "",
            # Untracked
            4: "",
            # Conflicting
            5: "",
        },
        "brackets": {
            0: "",
            1: "",
            2: "",
            3: "",
            4: "",
            5: "",
        },
    }

    for group, colorset in colors.items():
        pass

    with open(highlights_file, 'w') as file:
        file.write(contents)
    return
