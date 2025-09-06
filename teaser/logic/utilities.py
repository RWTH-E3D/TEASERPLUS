# created June 2015
# by TEASER4 Development Team

"""Utilities: Collection of all utility functions that are useful in several
classes
"""

import os
import shutil
import operator
import datetime
from pathlib import Path

ops = {"/": operator.truediv}


def check_and_fix_case_collisions(prj, export_root: str = None) -> Path | None:
    """
    Scan prj.buildings for names that collide on a case-insensitive FS.
    If duplicates are found (e.g. 'ABCD' vs 'abcd'), the *later* one
    gets a suffix '_<n>' to make it unique.

    Writes a short log file with the changes.
    Returns the path to the log if changes were made, else None.
    """
    seen = {}
    changes = []
    for b in prj.buildings:
        raw = str(b.name)
        key = raw.lower()
        if key not in seen:
            seen[key] = raw
            continue
        # collision → adjust this one
        counter = 1
        new = f"{raw}_{counter}"
        while new.lower() in seen:
            counter += 1
            new = f"{raw}_{counter}"
        b.name = new
        seen[new.lower()] = new
        changes.append((raw, new))

    # log to file
    base = Path(export_root) if export_root else Path(get_default_path())
    pkg_root = base / prj.name
    create_path(str(pkg_root))
    log_path = pkg_root / "case_name_corrections.txt"

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"[{ts}] Case-insensitive name corrections for project '{prj.name}'"]
    lines += [f"{old} -> {new}" for old, new in changes]
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n")

    print(f"[teaser.utilities] {len(changes)} building name(s) corrected; log at: {log_path}")
    return log_path

def celsius_to_kelvin(value):
    try:
        f_value = float(value)
    except TypeError:
        f_value = 0
    return f_value + 273.15


def create_path(path):
    """Create a folder.

    Creates a new folder.

    Parameters
    ----------
    path : str

    """
    path = os.path.normpath(path)
    # if directory exists change into that directory
    if(os.path.isdir(path)):
        return path
    else:
        if not os.path.exists(path):
            os.makedirs(path)
    return path


def get_default_path():
    """Function to construct default path to OutputData folder
    This function constructs the default path to the OutputData folder

    """

    home_path = os.path.expanduser('~')

    teaser_default_path = os.path.join(home_path, 'TEASEROutput')

    # directory = os.path.dirname(__file__)
    # src = "teaser"
    # last_index = directory.rfind(src)
    # teaser_default_path = os.path.join(directory[:last_index], "teaser",
    # "OutputData")

    return teaser_default_path.replace('\\', '/')


def get_full_path(rel_path):
    """Helperfunction to construct pathes to files within teaser.

    Parameters
    ----------
    rel_path : str
        Relative path beginning from teaser source folder including
        filename

    Returns
    ----------
    full_path : str

    """

    directory = os.path.dirname(__file__)
    src = "teaser"
    last_index = directory.rfind(src)
    first_path = os.path.join(directory[:last_index], "teaser")
    full_path = os.path.join(first_path, rel_path)

    return full_path


def clear_directory(dir_path=None):
    """Function to delete all files inside a directory.

    Parameters
    ----------
    dir_path : str
        Path of directory to be deleted. By default the teaser default
        directory is cleared

    """

    if dir_path is None:
        dir_path = get_default_path()
    else:
        pass

    if os.path.exists(dir_path):
        for file in os.listdir(path=dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                os.remove(os.path.join(dir_path, file))
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        print('The directory path does not exist.')


def division_from_json(ordereddict):
    """
    function to transform the output of division in json after loading to
    python into float values

    Parameters
    ----------
    ordereddict : output of the json load of arguments like
    "persons": {"/":[1,15]}

    """

    if len(ordereddict) == 1:
        for op, values in ordereddict.items():
            if op == '/':
                quotient = ops[op](values[0], values[1])
                return quotient
            else:
                raise ValueError('%s not supported, only divions (/)', op)
    else:
        raise ValueError('%s has len > 1', ordereddict)
