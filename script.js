require(["esri/Map", "esri/views/MapView"], function(Map, MapView) {

  const map = new Map({
    basemap: "streets"
  });

  const view = new MapView({
    container: "viewDiv",
    map: map,
    center: [51.5310, 25.2854],
    zoom: 10
  });

});