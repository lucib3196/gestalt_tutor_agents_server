from pathlib import Path

# Note only run this file when you need to clean
path = Path(r"data\me118").resolve()
class_name = path.stem
class_name = path.stem
for p in path.iterdir():
    if p.is_file():
        new_name = f"{class_name}_{p.stem}{p.suffix}"
        new_path = p.with_name(new_name)
        p.rename(new_path)
        print(f"Renamed: {p.name} -> {new_name}")
