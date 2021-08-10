module.exports = (chartObj, intent) => {
  switch (intent) {
    case "bar":
      chartObj.charts.spec.mark = "bar";
      return chartObj;
    case "line":
      chartObj.charts.spec.mark = {
        type: "line",
        point: true,
      };
      return chartObj;
    // case "scatter":
    //   chartObj.charts.spec.mark = "point";
    //   return chartObj;
    // case "heatmap":
    //   chartObj.charts.spec.mark = "rect";
    //   return chartObj;
    // case "parallelCoordinates":
    //   chartObj.charts.spec.mark = "line";
    //   return chartObj;
    case "map":
      chartObj.charts.spec.mark = { type: "geoshape", stroke: "black" };
  }
  return chartObj;
};
