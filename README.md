Get `vips`:

    apt install libvips-tools

Get the metadata:

    wget https://github.com/xsalazar/emoji-kitchen-backend/raw/refs/heads/main/app/metadata.json
    jq . metadata.json > metadata-pretty.json

Download the images:

    jq -r '.. | select(.isLatest?) | .gStaticUrl' metadata.json | sort | uniq > urls.txt
    python3 download.py

Find a few weird images that libvips doesn't like:

    fd -t f -x identify > identities.txt
    # find non-sRGB colorspaces:
    # (there were none)
    grep -v sRGB identities.txt
    # find colormaps / indexed palettes such as "252c":
    # (they identify with an extra column)
    awk 'NF!=9' identities.txt
    # back up the originals before fixing:
    cp <bad>{,-original}.png

Fix the weird images in GIMP by opening, adding transparency (even just a single pixel if necessary), and re-exporting with default PNG settings.

(Can also fix with `convert bad.png -define png:color-type=2 tmp.png` and `convert tmp.png -remap good.png fixed.png` but it's annoying and confusing.)

Make 1/4 scale versions of all the images, to keep final size somewhat reasonable:
**TODO** try 1/2 scale instead? 1/4 is a bit pixelated

    fd -g '*.png' -E '*-sm*.png' -x vips resize {} {.}-sm.png 0.25

(Note that `convert -resize` can change color palettes, hence using `vips resize`.)

Generate URL data for the website and a script to build the giant image:

    python grid.py metadata.json urls.js build.sh

Make the giant image and then the deep zoom tiles:

    bash build.sh
    vips dzsave /tmp/griddle/grid-sm.png deepgrid-sm --suffix .webp
