Get the metadata:

    wget https://github.com/xsalazar/emoji-kitchen-backend/raw/refs/heads/main/app/metadata.json
    jq . metadata.json > metadata-pretty.json

Download the images:

    jq -r '.. | .gstaticUrl? // empty' metadata.json | sort | uniq > urls.txt
    python3 download.py

(Note that we could exclude isLatest==false images, but that would only reduce downloads by <10%, and who knows, the old ones could be interesting.)

Organize the grid of images:

    ...

Make the giant image and the Deep Zoom Image:

    apt install libvips-tools
    vips arrayjoin ...
    vips dsave ...

Serve the deep zoom image:

    ...
