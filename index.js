(() => {
  const INITIAL_ZOOM = 0.25;
  const MIN_CLICK_ZOOM = 0.2;

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
    const alwaysOpen = true; // never use share dialog, for now
    if (alwaysOpen || !(navigator.canShare && navigator.share)) {
      // can't share, open in new tab instead
      window.open(url);
      return;
    }

    const response = await fetch(url);
    const blob = await response.blob();
    const data = {
      files: [new File([blob], "emoji-griddle.png", { type: "image/png" })],
    };
    // TODO how to get image preview when sharing in iOS/Safari?

    if (!navigator.canShare(data)) {
      // can't share, open in new tab instead
      console.log("!navigator.canShare", data);
      window.open(url);
      return;
    }

    navigator.share(data);
  };

  const viewer = OpenSeadragon({
    id: "griddle",
    // TODO put data prefix in a constant, and also use for urls.js
    // TODO switch between repo-a and repo-b, for more seamless updates
    tileSources: "https://hrldcpr.github.io/emoji-griddle-data/deepgrid-sm.dzi",
    showNavigationControl: false,
    maxZoomLevel: 400,
    // TODO gestureSettingsTouch and gestureSettingsMouse
  });

  viewer.addHandler("open", () => {
    // start zoomed in at a random spot
    // (waiting for 'open' event ensures that viewport is ready)
    viewer.viewport
      .panTo(
        {
          x: 0.1 + 0.8 * Math.random(),
          y: 0.1 + 0.8 * Math.random(),
        },
        true,
      )
      .zoomTo(viewer.viewport.imageToViewportZoom(INITIAL_ZOOM), null, true);
  });

  viewer.addHandler("canvas-click", (e) => {
    if (!e.quick) return; // not really a click

    const z = viewer.viewport.viewportToImageZoom(viewer.viewport.getZoom());
    if (z < MIN_CLICK_ZOOM) return; // ignore clicks when too zoomed out

    e.preventDefaultAction = true; // prevent zoom on desktop

    const p = viewer.viewport.viewerElementToImageCoordinates(e.position);
    const url = getUrl(p.x, p.y);
    if (url) shareImage(url);
  });

  // TODO easter egg if you (double?)click on self-combo, takes you to lazy-loaded long vertical scroll page for that emoji
})();
