(() => {
  const urlKey = (k) =>
    // rehydrate the keys, which are stored without 'u':
    k
      .split("-")
      .map((s) => `u${s}`)
      .join("-");

  const getUrl = (px, py) => {
    const urls = window.EMOJI_GRIDDLE_URLS;
    if (!urls) {
      console.log("urls not loaded");
      return;
    }
    const { pixels, prefix, dates, keys, suffix, grid } = urls;

    let [x, y] = [Math.floor(px / pixels), Math.floor(py / pixels)];
    // only the lower-left half of grid is stored, since it's symmetrical:
    if (y < x) [y, x] = [x, y];
    if (x < 0 || y >= keys.length) {
      console.log("out of bounds", { x, y });
      return;
    }

    let url = grid[y][x];
    // first character encodes the date:
    url = `${dates[url[0]]}/${url.substring(1)}`;
    // X and Y encode the two emoji keys:
    url = url.replaceAll("X", urlKey(keys[x])).replaceAll("Y", urlKey(keys[y]));
    // add prefix and suffix
    return `${prefix}${url}${suffix}`;
  };

  const shareImage = async (url) => {
    if (!(navigator.canShare && navigator.share)) {
      // can't share, open in new tab instead
      window.open(url);
      return;
    }

    const response = await fetch(url);
    const blob = await response.blob();
    const data = {
      files: [new File([blob], "emoji-griddle.png", { type: "image/png" })],
    };

    if (!navigator.canShare(data)) {
      // can't share, open in new tab instead
      console.log("!navigator.canShare", data);
      window.open(url);
      return;
    }

    navigator.share(data);
  };

  const viewer = OpenSeadragon({
    id: "openseadragon1",
    tileSources: "../emoji-griddle-data/deepgrid-sm.dzi",
    showNavigationControl: false,
    maxZoomLevel: 400,
  });

  viewer.addHandler("canvas-click", (e) => {
    if (!e.quick) return; // not really a click
    e.preventDefaultAction = true; // prevent zoom on desktop
    const p = viewer.viewport.viewerElementToImageCoordinates(e.position);
    const url = getUrl(p.x, p.y);
    if (url) shareImage(url);
  });
})();
