import argparse
import json
import sys

DIR_PREFIX = "www.gstatic.com/android/keyboard/emojikitchen"
URL_PREFIX = f"https://{DIR_PREFIX}/"
URL_SUFFIX = ".png"
TMP_DIR = "/tmp/griddle"
EMPTY_PNG = f"{TMP_DIR}/transparent.png"
PIXELS = 134  # (full scale is 535px, 1/4 scale is 134px)

parser = argparse.ArgumentParser()
parser.add_argument("metadata_path", help="metadata.json input file")
parser.add_argument("urls_path", help="urls.js output file")
parser.add_argument("script_path", help="build.sh output file")
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
        f.write(
            f'" {TMP_DIR}/{row_path} --hspacing {PIXELS} --vspacing {PIXELS} --halign centre --valign centre\n'
        )

    f.write(f"cd {TMP_DIR}\n")
    f.write(f'vips arrayjoin "{" ".join(row_paths)}" grid-sm.png --across 1\n')

# encode dates as a single character, from my arbitrary list:
# (sorting is unnecessary but hey why not)
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
dates = dict(zip(chars, sorted({p.split("/", 1)[0] for row in grid for p in row if p})))
date_chars = {d: c for c, d in dates.items()}

half_grid = []
for y in range(n):
    row = []
    for x in range(y + 1):  # only store lower-left half of symmetric grid
        path = grid[y][x]

        if path is None:
            row.append(0)  # replace None with 0 because it's shorter than "" or null
            continue

        # replace date with its one-character code:
        date, _ = path.split("/", 1)
        path = path.replace(f"{date}/", date_chars[date])

        # replace the current emoji codes with "X" and "Y":
        # (json keys look like e.g. 2705 or 263a-fe0f but urls look like u2705 or u263a-ufe0f)
        ux = "-".join(f"u{k}" for k in keys[x].split("-"))
        uy = "-".join(f"u{k}" for k in keys[y].split("-"))
        path = path.replace(ux, "X").replace(uy, "Y")

        # remove .png suffix:
        path = path.replace(URL_SUFFIX, "")

        row.append(path)
    half_grid.append(row)

# TODO XXX all left-facing moon urls are broken??

print(f"writing url js {args.urls_path}...")
with open(args.urls_path, "w") as f:
    f.write("window.EMOJI_GRIDDLE_URLS=")
    json.dump(
        {
            "pixels": PIXELS,
            "prefix": URL_PREFIX,
            "dates": dates,
            "keys": keys,
            "suffix": URL_SUFFIX,
            "grid": half_grid,
        },
        f,
        separators=(",", ":"),
    )
    f.write(";\n")
