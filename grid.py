import argparse
import json
import sys

DIR_PREFIX = "www.gstatic.com/android/keyboard/emojikitchen"
URL_PREFIX = f"https://{DIR_PREFIX}/"
URL_SUFFIX = ".png"
TMP_DIR = "/tmp/griddle"
EMPTY_PNG = f"{TMP_DIR}/transparent.png"

parser = argparse.ArgumentParser()
parser.add_argument("metadata_path", help="metadata.json input file")
parser.add_argument("script_path", help="build.sh output file")
parser.add_argument("urls_path", help="urls.json output file")
args = parser.parse_args()

print(f"reading metadata {args.metadata_path}...")
with open(args.metadata_path) as f:
    metadata = json.load(f)
data = metadata["data"]
keys = sorted(data, key=lambda k: data[k]["gBoardOrder"])
n = len(keys)

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
            print(f"FAIL {x}*{y}={grid[x][y]} != {y}*{x}={grid[y][x]}")
            sys.exit(1)
        # only one value, can fix automatically:
        print(f"WARN fixing {x}*{y}={grid[x][y]} != {y}*{x}={grid[y][x]}")
        grid[x][y] = grid[y][x] = grid[x][y] or grid[y][x]
print(f"PASS symmetric {len(grid)}x{len(grid[0])}")

print(f"writing build script {args.script_path}...")
with open(args.script_path, "w") as f:
    f.write(f"echo {n}x{n}\n")
    f.write(f"mkdir -p {TMP_DIR}\n")
    f.write(f"cp transparent*.png {TMP_DIR}\n")
    f.write(f"cd {DIR_PREFIX}\n")

    row_paths = []
    for y in range(n):
        row_path = f"row-{y:03d}.png"
        row_paths.append(row_path)
        f.write(f"echo {row_path} {keys[y]}\n")

        # note that imagemagick `convert ... +append out.png` seems to have a default width/height limit of 16000px
        # so we use vips instead
        f.write('vips arrayjoin "')
        for x in range(n):
            path = grid[y][x] or EMPTY_PNG
            path = path.replace(".png", "-sm.png")  # use small images, for now
            f.write(f"{path} ")
        # note we only need to specify hspacing and vspacing because we build each row separately;
        # if we did a giant single arrayjoin for the entire grid, it would figure them out correctly:
        # (full scale is 535px, 1/4 scale is 134px)
        f.write(
            f'" {TMP_DIR}/{row_path} --hspacing 134 --vspacing 134 --halign centre --valign centre\n'
        )

    f.write(f"cd {TMP_DIR}\n")
    f.write(f'vips arrayjoin "{" ".join(row_paths)}" grid-sm.png --across 1\n')

# for smallest file:
# - only store lower-left half of symmetric grid
# - remove .png suffices
# - replace None with 0 because it's shorter than "" or null
half_grid = []
for y in range(n):
    row = []
    for x in range(y + 1):
        path = grid[y][x]
        row.append(path.replace(URL_SUFFIX, "") if path else 0)
    half_grid.append(row)

print(f"writing url json {args.urls_path}...")
with open(args.urls_path, "w") as f:
    json.dump(
        {"prefix": URL_PREFIX, "suffix": URL_SUFFIX, "grid": half_grid},
        f,
        separators=(",", ":"),
    )
