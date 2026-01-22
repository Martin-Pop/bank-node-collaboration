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

def get_base_paths():
    """
    Gets a dictionary with paths to key resources.
    'exe_dir': The directory where the executable (or entry script) is. Used to pathfind to configs and logs
    'data_dir': The directory where bundled resources (public/templates) live.
    :return: dictionary with folders for root path, config path, public path
    """
    app_root = get_app_root()

    if getattr(sys, 'frozen', False):
        # dir where pyinstaller set code extraction (with --onedir mode its the __internal)
        data_dir = Path(getattr(sys, '_MEIPASS', app_root))
        external_dir = app_root
    else:
        data_dir = app_root / "src/web"
        external_dir = app_root

    return {
        "config_folder": external_dir / "config",
        "public_folder": data_dir / "public",
        "root": external_dir,
    }

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