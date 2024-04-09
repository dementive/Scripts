import os

"""
    Minify Imperator script files or folders
    Removes all comments and line breaks also doens't allow any double spaces
    Line breaks are still allowed for event namespaces because they don't work without them
    The on_action folder is skipped because minifying on_action files breaks the game

    You probably don't want to run this script from inside of your mod folder as it will do some funky things.
"""

included_directories = [
    "common",
    "culture_decisions",
    "decisions",
    "events",
    "map_data",
    "setup",
]


def minify_text(text):
    lines = text.splitlines()

    minified_lines = [
        " ".join(line.split("#")[0].split()) for line in lines if line.split("#")[0].strip() != ""
    ]

    minified_lines = list(
        map(
            lambda line: line.replace("namespace", "\nnamespace") + "\n" if "namespace" in line else line,
            minified_lines,
        )
    )

    return " ".join(minified_lines)


def minify_all(input_dir):
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for dirpath, dirnames, filenames in os.walk(input_dir):
        if "on_action" in dirpath:
            continue
        if not any(s in dirpath for s in included_directories):
            continue

        for filename in [x for x in filenames if x.endswith(".txt")]:
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "r", encoding="utf-8-sig") as file:
                contents = file.read()

            minified_contents = minify_text(contents)

            # Create a similar directory structure in output_dir
            rel_dir = os.path.relpath(dirpath, input_dir)
            output_dirpath = os.path.join(output_dir, rel_dir)
            if not os.path.exists(output_dirpath):
                os.makedirs(output_dirpath)

            with open(os.path.join(output_dirpath, filename), "w", encoding="utf-8-sig") as file:
                file.write(minified_contents)


def minify_file(input_filepath):
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.basename(input_filepath)
    with open(input_filepath, "r") as file:
        contents = file.read()

    minified_contents = minify_text(contents)

    with open(os.path.join(output_dir, filename), "w") as file:
        file.write(minified_contents)


if __name__ == "__main__":
    # minify_file(
    #     "/home/nathan/.local/share/Paradox Interactive/Imperator/mod/ImperatorFMO/events/subject_focus_events.txt"
    # )

    minify_all("C:\\Users\\demen\\Documents\\Paradox Interactive\\Imperator\\mod\\ImperatorFMO")
