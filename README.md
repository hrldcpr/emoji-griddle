Get `vips`:

    apt install libvips-tools

Get the metadata:

    wget https://github.com/xsalazar/emoji-kitchen-backend/raw/refs/heads/main/app/metadata.json
    jq . metadata.json > metadata-pretty.json

Download the images:

    jq -r '.. | select(.isLatest?) | .gStaticUrl' metadata.json | sort | uniq > urls.txt
    python3 download.py

Find a few weird images that libvips doesn't like:

    cd www.gstatic.com
    fd -t f -E '*-sm.png' -x identify > identities.txt
    # find images with weird sizes:
    # (we don't actually need to do anything about these, but it's worth keeping an eye on them)
    grep -v '53[45]x53[45]' identities.txt
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

    fd -g '*.png' -E '*-sm.png' -x bash ../shrink.bash {}

(Note that `convert -resize` can change color palettes, hence using `vips resize`.)

Generate URL data for the website and a script to build the giant image:

    cd ..
    python grid.py metadata.json urls.js build.sh

Make the giant image and then the deep zoom tiles:

    bash build.sh
    cd ..
    mkdir emoji-griddle-data-<N>
    cd emoji-griddle-data-<N>
    mv ../emoji-griddle/urls.js .
    vips dzsave /tmp/griddle/grid-sm.png deepgrid-sm --suffix .webp
    git init
    git add .
    git commit -m 'data'

And finally, we deploy:

- make a new github repo (since we don't want to maintain history since the files are huge)
- `git push` (takes a while)
- enable github pages (takes a while)
- update the references to `emoji-griddle-data-<N>/` in index.html and index.js
- commit with a reference to the `emoji-kitchen-backend` commit that the metadata came from
- once things have settled (maybe wait at least a day, for caches to busy), can delete previous data repo
