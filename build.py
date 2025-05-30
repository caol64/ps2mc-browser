import tomli as tomllib
import PyInstaller.__main__
from pathlib import Path

config = tomllib.loads(Path("pyproject.toml").read_text())

pyi_cfg = config["tool"]["pyinstaller"]

PyInstaller.__main__.run([
    f"--name={pyi_cfg['app_name']}",
    "--windowed" if pyi_cfg.get("windowed") else "",
    "--onefile" if pyi_cfg.get("onefile") else "",
    *[f"--add-data={d}" for d in pyi_cfg["add_data"]],
    *[f"--hidden-import={h}" for h in pyi_cfg["hidden_imports"]],
    pyi_cfg["entry_point"]
])
