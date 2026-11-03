import pathlib
import sys

COMFY_ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
PACKAGE_ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMFY_ROOT))
sys.path.insert(0, str(PACKAGE_ROOT))
