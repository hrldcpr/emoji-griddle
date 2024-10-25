import json

DIR_PREFIX = "www.gstatic.com/android/keyboard/emojikitchen"
URL_PREFIX = f"https://{DIR_PREFIX}/"
TMP_DIR = "/tmp/griddle"

with open("metadata.json") as f:
    metadata = json.load(f)

data = metadata["data"]

keys = sorted(data, key=lambda k: data[k]["gBoardOrder"])
print(f"echo {len(keys)}x{len(keys)}")

print(f"mkdir -p {TMP_DIR}")
print(f"cp transparent*.png {TMP_DIR}")
print(f"cd {DIR_PREFIX}")

row_paths = []
for i, y in enumerate(keys):
    row_path = f"row-{i:03d}.png"
    row_paths.append(row_path)
    print(f"echo {row_path} {y}")

    # note that imagemagick `convert ... +append out.png` seems to have a default width/height limit of 16000px
    # so we use vips instead
    print('vips arrayjoin "', end="")
    for x in keys:
        (path,) = [
            d["gStaticUrl"].replace(URL_PREFIX, "")
            for d in data[y]["combinations"].get(x, [])
            if d["isLatest"]
        ] or [f"{TMP_DIR}/transparent.png"]
        print(path.replace(".png", "-sm.png"), end=" ")
    # note we only need to specify hspacing and vspacing because we build each row separately;
    # if we did a giant single arrayjoin for the entire grid, it would figure them out correctly:
    # (full scale is 535px, 1/4 scale is 134px)
    print(
        f'" {TMP_DIR}/{row_path} --hspacing 134 --vspacing 134 --halign centre --valign centre'
    )

print(f"cd {TMP_DIR}")
print(f'vips arrayjoin "{" ".join(row_paths)}" grid-sm.png --across 1')
