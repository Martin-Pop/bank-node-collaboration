import sys
from pathlib import Path

def get_app_root() -> Path:
    """
    Returns app root folder
    - if .exe (frozen) returns file where executable is located.
    - if its a script, returns src parent.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent.parent

def resolve_path(user_path: str) -> str:
    """
    Resolves path by checking if its absolute otherwise its relative path to root
    :param user_path: path to resolve
    """
    path_obj = Path(user_path)

    if path_obj.is_absolute():
        return str(path_obj)

    full_path = get_app_root() / path_obj
    return str(full_path)