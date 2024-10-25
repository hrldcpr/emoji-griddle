const viewer = OpenSeadragon({
  id: "openseadragon1",
  tileSources: "deepgrid-sm.dzi",
  showNavigationControl: false,
  maxZoomLevel: 400,
});
viewer.addHandler("canvas-click", function (e) {
  e.preventDefaultAction = true;
  const { x, y } = viewer.viewport.viewerElementToImageCoordinates(e.position);

  console.log("Clicked at image coordinates:", x, y);
});
