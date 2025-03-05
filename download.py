import pathlib
import subprocess
import sys
import time

skip = int(sys.argv[1]) if len(sys.argv) > 1 else 0

for i, line in enumerate(open("urls.txt")):
    if i < skip:
        continue

    if pathlib.Path(line.strip().removeprefix("https://")).exists():
        print("#", i)
        continue

    # TODO retry a couple times
    subprocess.run(
        ["wget", "--quiet", "--force-directories", line.strip()]
    ).check_returncode()
    print(i)
    time.sleep(0.5)
