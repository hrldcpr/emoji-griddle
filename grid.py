import json

with open("metadata.json") as f:
    metadata = json.load(f)

data = metadata["data"]

keys = sorted(data, key=lambda k: data[k]["gBoardOrder"])
print(f"echo {len(keys)}x{len(keys)}")

row_paths = []
print("cd www.gstatic.com/android/keyboard/emojikitchen")
print("mkdir -p griddle")
for i, y in enumerate(keys):
    row_path = f"{i:03d}.png"
    row_paths.append(row_path)
    print(f"echo {row_path} {y}")

    # note that imagemagick `convert ... +append out.png` seems to have a default width/height limit of 16000px
    # so we use vips instead
    print('vips arrayjoin "', end="")
    for x in keys:
        (url,) = [
            d["gStaticUrl"] for d in data[y]["combinations"].get(x, []) if d["isLatest"]
        ] or ["griddle/transparent.png"]
        path = url.replace("https://www.gstatic.com/android/keyboard/emojikitchen/", "")
        print(path, end=" ")
    # note we only need to specify hspacing and vspacing because we build each row separately;
    # if we did a giant single arrayjoin for the entire grid, it would figure them out correctly:
    print(f'" griddle/{row_path} --hspacing 535 --vspacing 535 --halign centre --valign centre')

print("cd griddle")
print(f'vips arrayjoin "{' '.join(row_paths)}" grid.png --across 1')
