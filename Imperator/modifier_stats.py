"""
Python command line program to generate plots for analysis of modifier usage in Imperator: Rome.
This should help to balance out modifiers, compare the overall values of modifiers to other mods/vanilla, and get other insights into the usage of modifiers in your mod.
Requires both numpy and plotly python packages


CLI Usage:

`python modifier_stats.py -path "path/to/your/mod/directory"`

CLI Arguments:

-path: The full path to the mod you want to analyze the modifiers in. This can also be the path to the game files. This is the only required argument.
    Example: -path "path/to/your/mod/directory"

-dirs: List of relative paths to directories you want to analyze. Each directory should be seperated by a space.
    Example: -dirs "common/buildings" "common/laws" 

-plot: The type of plot to display
    Example: -plot Scatter
    Args: Vbar, Scatter, or Bubble
    Default: Bubble

-sortby: The main variable to display for the plot. Can be either 'uses' or 'value'. uses will have the graph compare the total uses of each modifier. value will compare the total value of the modifier.
    Example: -sortby uses
    Args: uses, value
    Default: value

-filterby: The secondary variable to display for the plot. Can be either 'uses' or 'value'. Filters value below -min and above -max out of the resulting plot.
    Example: -sortby uses
    Args: uses, value
    Default: value

-min: The minimum value the variable specified in -filterby is allowed to be.
    Example: -min -25
    Default: -6

-max: The maximum value the variable specified in -filterby is allowed to be.
    Example: -max 15
    Default: 10

"""


import os
import re
import argparse
from typing import Dict, List, Any

import plotly.graph_objects as go
import numpy as np


DEFAULT_ANALYSIS_DIRS = {
    "common\\buildings\\",
    "common\\inventions\\",
    "common\\laws\\",
}

BANNED_LIST = {
    "max",
    "duration",
    "age",
    "election_term_duration",
    "time",
    "value",
    "max_amount",
    "factor",
    "cost",
    "from_ruler_family",
    "war_exhaustion",
    "remove_all_positions",
    "subtract",
    "republic_to_monarchy_law_variable_effect",
    "republic_to_monarchy_law_change_effect",
    "country_dictatorship_party_trigger",
    "switch_government_type_event_clearup_effect",
    "always",
    "navy",
    "keystone",
    "multiply",
}

BANNED_PREFIXES = {
    "add",
    "is_",
    "has_",
    "can_",
}


class ModifierData:
    def __init__(self, name: str, value: str, file: str, line: int):
        self.name = name
        self.file = os.path.basename(file)
        self.line = line
        self.value = value


class Modifier:
    def __init__(
        self, name: str, total_value: float, modifier_data: List[ModifierData]
    ):
        self.name = name
        self.total_value = round(total_value, 2)
        self.modifier_data = modifier_data
        self.total_uses = len(modifier_data)

    def print(self):
        print(f"Modifier Name: {self.name}\nModifier Value: {self.total_value}\n")

    def get_modifier_data_string(self):
        string = str()
        for i in self.modifier_data:
            string += f"File: {i.file} - Line: {i.line} - Value: {i.value}<br>"
        return string


base_modifiers: Dict[str, List[ModifierData]]
base_modifiers = dict()


def get_filtered_data(modifier_data, filter_by, minimum, maximum):
    filtered_data = [
        x
        for x in modifier_data
        if float(minimum) <= getattr(x, f"total_{filter_by}") <= float(maximum)
    ]

    names = [x.name for x in filtered_data]
    values = [x.total_value for x in filtered_data]
    uses = [x.total_uses for x in filtered_data]
    sources = [x.get_modifier_data_string() for x in filtered_data]

    return (names, values, uses, sources)


def get_hover_template(customdata):
    return (
        "<b>Name</b>: %{customdata[0]}<br>"
        + "<b>Total Value</b>: %{customdata[1]}<br>"
        + "<b>Total Usage</b>: %{customdata[2]}<br>"
        + "<b>Sources</b>:<br>%{customdata[3]}"
        + "<extra></extra>"
    )


def get_color(value, max_value):
    """
    Generate a color based on the value's distance from 0.
    Values further from 0 will be more red.
    """
    # Normalize the value to the range [0, 1]
    normalized_value = abs(value) / max_value

    # Calculate the RGB values for red and green
    red = (225, 80, 80)
    orange = (225, 143, 51)

    # Interpolate between values, higher values will be red, lower will be orange.
    r = abs(int(orange[0] * (1 - normalized_value) + red[0] * normalized_value))
    g = abs(int(orange[1] * (1 - normalized_value) + red[1] * normalized_value))
    b = abs(int(orange[2] * (1 - normalized_value) + red[2] * normalized_value))

    # Return the color as a string in the format 'rgb(r, g, b)'
    return f"rgb({r}, {g}, {b})"


class Plots:
    def __init__(self, modifier_data, dirname, args):
        d = get_filtered_data(modifier_data, args.filterby, args.min, args.max)
        customdata = np.stack((d[0], d[1], d[2], d[3]), axis=-1)
        dirname = dirname.title()
        if dirname == "Game":
            dirname = "Base Game"
        self.Vbar = (
            go.Bar,
            {
                "y": d[1],
                "x": d[0],
                "customdata": customdata,
                "hovertemplate": get_hover_template(customdata),
            },
            {
                "xaxis": {"title": f"Total Modifier {args.sortby.title()}"},
                "yaxis": {"title": f"Modifier Names"},
                "title": f"{dirname} Modifier Values Bar Plot",
            },
        )
        self.Scatter = (
            go.Scatter,
            {
                "y": d[0],
                "x": d[1],
                "customdata": customdata,
                "mode": "markers",
                "marker": {"size": 15},
                "hovertemplate": get_hover_template(customdata),
            },
            {
                "xaxis": {"title": f"Total Modifier {args.sortby.title()}"},
                "yaxis": {"title": f"Modifier Names"},
                "title": f"{dirname} Modifier Values Scatter Plot",
            },
        )
        size = [abs(x) for x in d[1]]
        self.Bubble = (
            go.Scatter,
            {
                "y": d[0],
                "x": d[1],
                "customdata": customdata,
                "hovertemplate": get_hover_template(customdata),
                "mode": "markers",
                "marker": dict(
                    size=size,
                    color=[get_color(x, float(args.max)) for x in d[1]],
                    sizemode="area",
                    sizeref=2.0 * max(size) / (40.0**2),
                    sizemin=4,
                ),
            },
            {
                "xaxis": {"title": f"Total Modifier {args.sortby}"},
                "yaxis": {"title": f"Modifier Names"},
                "title": f"{dirname} Modifier Values Bubble Plot",
            },
        )
        if args.sortby.lower() == "uses":
            self.Bubble[1]["x"] = d[2]
            self.Scatter[1]["x"] = d[2]
            self.Vbar[1]["y"] = d[2]


def get_last_directory_name(path):
    normalized_path = os.path.normpath(path)
    last_directory_name = os.path.basename(normalized_path)
    return last_directory_name


def update_modifiers(modifiers) -> List[Modifier]:
    x = list()
    for i in modifiers:
        total_value = 0
        for j in modifiers[i]:
            value = int()
            if j.value == "yes":
                value = 1
            else:
                value = j.value
            total_value += float(value)
        x.append(Modifier(i, total_value, modifiers[i]))
    return x


def main(args):
    found_files = dict()
    path = args.path
    if not path.endswith("\\"):
        path += "\\"
    for i in args.dirs:
        if not i.endswith("\\"):
            i += "\\"
        found_files[i] = [path + i + x for x in os.listdir(path + i)]

    for i in found_files:
        for j in found_files[i]:
            handle_file(j)

    base_modifier_data = update_modifiers(base_modifiers)
    plot1 = Plots(base_modifier_data, get_last_directory_name(path), args)
    attr1 = getattr(plot1, args.plot)

    show_plot(attr1[0], attr1[1], attr1[2])


def handle_file(filepath):
    global base_modifiers, new_modifiers
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        modifier = handle_line(line)
        if modifier:
            name = modifier[0]
            banned = False
            if name in BANNED_LIST:
                banned = True
            for j in BANNED_PREFIXES:
                if j in name:
                    banned = True
            if banned:
                continue
            if name not in base_modifiers:
                base_modifiers[name] = [ModifierData(name, modifier[1], filepath, i)]
            else:
                base_modifiers[name].append(
                    ModifierData(name, modifier[1], filepath, i)
                )


def handle_line(line):
    modifier_found = re.search(
        r"([A-Za-z_0-9][A-Za-z_0-9]*)\s?=\s?(-?\d+\.?\d?\d?|yes)", line
    )
    if modifier_found:
        name = modifier_found.group(1)
        value = modifier_found.group(2)
        return (name, value)
    return False


def show_plot(Plot: type, kwargs: Dict[Any, Any], layout_kwargs):
    fig = go.Figure()
    fig.add_trace(Plot(**kwargs))
    fig.update_layout(**layout_kwargs)
    fig.show()


def is_valid_directory(parser, arg):
    if not os.path.isdir(arg):
        parser.error(f"The directory {arg} does not exist!")
    return arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A simple command-line program to compare Imperator Rome modifier values for comparative analysis."
    )
    parser.add_argument(
        "-path",
        help="The path to the game/mod directory.",
        type=lambda x: is_valid_directory(parser, x),
        required=True,
    )
    parser.add_argument(
        "-dirs",
        type=str,
        nargs="*",
        help="A list of directory paths relative to your mod of all the folders you want to analyze modifier values in.",
        default=DEFAULT_ANALYSIS_DIRS,
    )
    parser.add_argument(
        "-plot",
        help="The type of plot to display. Can be VBar, Scatter, or Bubble.",
        default="Bubble",
        choices=["Vbar", "Scatter", "Bubble"],
    )
    parser.add_argument(
        "-sortby",
        help="The main variable to display for the plot. Can be either 'uses' or 'value'. uses will have the graph compare the total uses of each modifier. value will compare the total value of the modifier.",
        default="value",
        choices=["value", "uses"],
    )
    parser.add_argument(
        "-filterby",
        help="The secondary variable to display for the plot. Can be either 'uses' or 'value'.",
        default="value",
        choices=["value", "uses"],
    )
    parser.add_argument(
        "-min",
        help="The minimum value to display on the plot.",
        default=-6,
    )
    parser.add_argument(
        "-max",
        help="The minimum value to display on the plot.",
        default=10,
    )
    args = parser.parse_args()

    
    for i in args.dirs:
        if not i.endswith("\\"):
            i += "\\"
        path = args.path
        if not path.endswith("\\"):
            path += "\\"
        directory = path + i
        if not os.path.isdir(directory):
            parser.error(f"The directory {directory} does not exist!")

    main(args)
