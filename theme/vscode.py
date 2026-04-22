from pathlib import Path
import json


def modify_vscode_settings(settings_file: Path,
                           colors: dict[str, list[str]]) -> None:
    settings = {}
    with open(settings_file, 'r') as file:
        settings = json.load(file)
    if settings == {}:
        raise ValueError("Could not extract JSON from settings file!")
# VSCODE UI COLORS
    vscode_ui_settings = settings["workbench.colorCustomizations"]
    theme_vscode_mapping: dict[str, dict[int, str | list[str]]] = {
        "basic": {
            0: [  # Background, darkest
                "editor.background",
                "editorCursor.background",
                "editorGroup.emptyBackground",
                "editorGroupHeader.tabsBackground",
                "editorGroupHeader.noTabsBackground",
                "tab.interactiveBackground",
                "panel.background",
                "editorWidget.background",
                "activityBar.background",
                "sideBar.background",
                "sideBarTitle.background",
                "sideBarSectionHeader.background",
                "menu.background",
                "quickInput.background",
                "titleBar.activeBackground",
                "titleBar.inactiveBackground",
                "statusBar.background"
            ],
            1: [  # Background, dark
                "tab.activeBackground",
                "panel.border",
                "editor.lineHighlightBackground",
                "editor.selectionBackground",
                "editorGroup.border",
                "editorGroupHeader.border",
                "editorGroupHeader.tabsBorder",
                "tab.border",
                "tab.unfocusedHoverBackground",
                "tab.hoverBackground",
                "editorWidget.border",
                "activityBar.border",
                "sideBar.border",
                "input.background",
                "checkbox.background",
                "settings.dropdownBackground",
                "dropdown.background",
                "dropdown.listBackground",
                "list.activeSelectionBackground",
                "list.inactiveSelectionBackground",
                "list.hoverBackground",
                "titleBar.border",
                "keybindingLabel.background",
                "statusBar.border"
            ],
            2: [  # Foreground, medium
                "editorLineNumber.foreground",
                "activityBar.inactiveForeground",
                "input.placeholderForeground",
                "dropdown.border",
                "list.deemphasizedForeground",
                "menu.separatorBackground",
                "menu.border",
                "pickerGroup.border",
                "widget.border",
                "titleBar.inactiveForeground",
                "keybindingLabel.border",
                "keybindingLabel.bottomBorder",
            ],
            3: [  # Foreground, light
                "foreground",
                "editorCursor.foreground",
                "editorLineNumber.activeForeground",
                "editorSuggestWidget.foreground",
                "tab.activeForeground",
                "activityBar.foreground",
                "sideBar.foreground",
                "sideBarTitle.foreground",
                "settings.dropdownForeground",
                "settings.textInputForeground",
                "settings.numberInputForeground",
                "list.focusForeground",
                "list.hoverForeground",
                "terminal.foreground",
                "menu.foreground",
                "quickInput.foreground",
                "titleBar.activeForeground",
                "search.resultsInfoForeground",
                "keybindingLabel.foreground",
            ],
            4: [  # Foreground, lightest
                "activityBarBadge.foreground",
                "badge.foreground",
                "input.foreground",
                "list.activeSelectionForeground"
            ]
        },
        "scrollbar": {
            0: [
                "scrollbarSlider.background",
                "scrollbarSlider.hoverBackground",
                "scrollbarSlider.activeBackground"
            ]
        },
        "highlight": {
            0: [  # Medium highlight
                "tab.inactiveForeground",
                "tab.unfocusedInactiveForeground",
                "menu.selectionBackground",
                "badge.background",
                "button.background",
                "button.hoverBackground",
                "terminalCommandDecoration.successBackground",
                "symbolIcon.fileForeground",
                "pickerGroup.foreground"
            ],
            1: [  # Bright highlight
                "focusBorder",
                "tab.activeBorderTop",
                "panelTitle.activeBorder",
                "terminal.tab.activeBorder",
                "activityBar.activeBorder",
                "textLink.foreground",
                "editorSuggestWidget.highlightForeground",
                "editorSuggestWidget.focusHighlightForeground",
                "panelTitleBadge.background",
                "activityBarBadge.background",
                "statusBarItem.remoteBackground"
            ],
            2: [  # Warning Color
                "editorWarning.foreground",
                "editorLightBulbAutoFix.foreground"
            ],
            3: [  # Error Color
                "errorForeground",
                "editorError.foreground",
                "problemsErrorIcon.foreground",
                "list.errorForeground"
            ],
        },
        "git": {
            0: [  # Added
                "gitDecoration.addedResourceForeground",
                "editorGutter.addedBackground",
            ],
            1: [  # Modified
                "gitDecoration.modifiedResourceForeground",
                "editorGutter.modifiedBackground"
            ],
            2: [  # Deleted
                "gitDecoration.deletedResourceForeground",
                "editorGutter.deletedBackground",
            ],
            3: "gitDecoration.ignoredResourceForeground",
            4: "gitDecoration.untrackedResourceForeground",
            5: "gitDecoration.conflictingResourceForeground",
        },
        "brackets": {
            0: "editorBracketHighlight.foreground1",
            1: "editorBracketHighlight.foreground2",
            2: "editorBracketHighlight.foreground3",
            3: "editorBracketHighlight.foreground4",
            4: "editorBracketHighlight.foreground5",
            5: "editorBracketHighlight.foreground6",
        },
        "ansi": {
            0: "terminal.ansiBlack",
            1: "terminal.ansiRed",
            2: "terminal.ansiGreen",
            3: "terminal.ansiYellow",
            4: "terminal.ansiBlue",
            5: "terminal.ansiMagenta",
            6: "terminal.ansiCyan",
            7: "terminal.ansiWhite",
            8: "terminal.ansiBrightBlack",
            9: "terminal.ansiBrightRed",
            10: "terminal.ansiBrightGreen",
            11: "terminal.ansiBrightYellow",
            12: "terminal.ansiBrightBlue",
            13: "terminal.ansiBrightMagenta",
            14: "terminal.ansiBrightCyan",
            15: "terminal.ansiBrightWhite",
        }
    }
    for color_group, colormap in theme_vscode_mapping.items():
        palette = colors[color_group]
        for color_index, settings_to_apply in colormap.items():
            if color_index > len(palette):
                color_index = -1
            if isinstance(settings_to_apply, list):
                for single_setting in settings_to_apply:
                    vscode_ui_settings[single_setting] = palette[color_index]
            else:
                vscode_ui_settings[settings_to_apply] = palette[color_index]

# LANGUAGE SYNTAX HIGHLIGHTING
    syntax_color_settings = settings["editor.tokenColorCustomizations"]["textMateRules"]
    theme_language_mapping = {
        "Normal": ["source", "keyword.operator", "markup.text"],
        "Comment": [
            "comment",
            "comment.in_line",
            "comment.block.documentation",
            "string.quoted.docstring.multi.python"
        ],
        "Numeric": "constant.numeric",
        "String": "string",
        "Keyword": [
            "keyword",
            "meta.preprocessor",
            "keyword.control",
            "storage.type",
            "keyword.operator.quantifier.regexp",
        ],
        "Constant": [
            "constant.language",
            "constant.character.python",
            "storage.type.format.python",
            "keyword.operator.logical.python",
            "constant.character.format.placeholder.other.python"
        ],
        "Variable": [
            "variable",
            "support.type.property-name",
            "support.variable",
            "entity.other.attribute"
        ],
        "Function": [
            "entity.name.function",
            "support.function",
            "support.function.magic.python"  # Includes magic/dunder methods
        ],
        "Types": [
            "entity.name.type",
            "entity.name.namespace",
            "heading.1.markdown",
            "heading.2.markdown",
            "heading.3.markdown",
            "heading.4.markdown",
            "heading.5.markdown",
            "heading.6.markdown",
        ],
        "Constant Name": [
            "variable.other.enummember",
            "variable.other.constant",
            "string.regexp.quoted.single.python",
            "string.regexp.quoted.double.python",
            "punctuation.character.set.begin.regexp",
            "punctuation.character.set.end.regexp",
            "keyword.operator.negation.regexp",
            "constant.character.set.regexp",
            "support.other.parenthesis.regexp"
        ],
        "Language Variable": "variable.language.python"
    }
    syntax_color_settings.clear()
    for group, color in colors["language"].items():
        settings_group = {
            "scope": theme_language_mapping[group],
            "settings": {"foreground": color}
        }
        syntax_color_settings.append(settings_group)
    output = settings_file.with_name(settings_file.stem + "_out.json")
    with open(output, 'w') as file:
        json.dump(settings, file)
    return
