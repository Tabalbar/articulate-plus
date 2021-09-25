module.exports = (chart, intent) => {
  switch (intent) {
    case "bar":
      chart.spec.mark = "bar";
      return chart;
    case "line":
      chart.spec.mark = {
        type: "line",
        point: { size: 100 },
      };
      return chart;
    // case "scatter":
    //   chart.spec.mark = "point";
    //   return chart;
    case "heatmap":
      chart.spec.mark = "rect";
      return chart;
    // case "parallelCoordinates":
    //   chart.spec.mark = "line";
    //   return chart;
    case "map":
      chart.spec.mark = { type: "geoshape", stroke: "black" };
  }
  return chart;
};
