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
    code = subprocess.run(
        ["wget", "--quiet", "--force-directories", line.strip()]
    ).returncode
    if code == 0:
        print(i)
    elif code == 8:
        print("NOT FOUND", line.strip())
    else:
        raise f"wget exit code={code} for {line.strip()}"
    time.sleep(0.5)
