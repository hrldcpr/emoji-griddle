import json
import sys

DIR_PREFIX = "www.gstatic.com/android/keyboard/emojikitchen"
URL_PREFIX = f"https://{DIR_PREFIX}/"
TMP_DIR = "/tmp/griddle"
EMPTY_PNG = f"{TMP_DIR}/transparent.png"

with open("metadata.json") as f:
    metadata = json.load(f)
data = metadata["data"]
keys = sorted(data, key=lambda k: data[k]["gBoardOrder"])
n = len(keys)

print(f"echo {n}x{n}")
print(f"mkdir -p {TMP_DIR}")
print(f"cp transparent*.png {TMP_DIR}")
print(f"cd {DIR_PREFIX}")

grid = []
for ky in keys:
    row = []
    for kx in keys:
        (path,) = [
            d["gStaticUrl"].replace(URL_PREFIX, "")
            for d in data[ky]["combinations"].get(kx, [])
            if d["isLatest"]
        ] or [None]
        row.append(path)
    grid.append(row)

# sanity check that grid is symmetrical:
for y in range(n):
    for x in range(n):
        if grid[x][y] == grid[y][x]:
            continue
        if (grid[x][y] is not None) and (grid[y][x] is not None):
            # two different values, need to address manually:
            print(f"FAIL {x}*{y}={grid[x][y]} != {y}*{x}={grid[y][x]}", file=sys.stderr)
            sys.exit(1)
        # only one value, can fix automatically:
        print(
            f"WARN fixing {x}*{y}={grid[x][y]} != {y}*{x}={grid[y][x]}",
            file=sys.stderr,
        )
        grid[x][y] = grid[y][x] = grid[x][y] or grid[y][x]
print(f"PASS symmetric {len(grid)}x{len(grid[0])}", file=sys.stderr)

row_paths = []
for y in range(n):
    row_path = f"row-{y:03d}.png"
    row_paths.append(row_path)
    print(f"echo {row_path} {keys[y]}")

    # note that imagemagick `convert ... +append out.png` seems to have a default width/height limit of 16000px
    # so we use vips instead
    print('vips arrayjoin "', end="")
    for x in range(n):
        path = grid[y][x] or EMPTY_PNG
        path = path.replace(".png", "-sm.png")  # use small images, for now
        print(path, end=" ")
    # note we only need to specify hspacing and vspacing because we build each row separately;
    # if we did a giant single arrayjoin for the entire grid, it would figure them out correctly:
    # (full scale is 535px, 1/4 scale is 134px)
    print(
        f'" {TMP_DIR}/{row_path} --hspacing 134 --vspacing 134 --halign centre --valign centre'
    )

print(f"cd {TMP_DIR}")
print(f'vips arrayjoin "{" ".join(row_paths)}" grid-sm.png --across 1')
