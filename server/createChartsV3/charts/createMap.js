const covidColors = require("./covidHelpers/covidColors");
const covidSort = require("./covidHelpers/covidSort");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
const createChartTemplate = require("./createChartTemplate");

module.exports = (
  chartMsg,
  extractedHeaders,
  extractedFilteredValues,
  headerFrequencyCount,
  filterFrequencyCount
) => {
  let chart = createChartTemplate(
    chartMsg,
    headerFrequencyCount,
    filterFrequencyCount
  );
  chart.transform.push({
    lookup: "map",
    from: {
      data: {
        url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
        format: { type: "topojson", feature: "counties" },
      },
      key: "id",
    },
    as: "geo",
  });
  chart = createTransform(chart, chartMsg, extractedFilteredValues);

  let obj = {
    data: chart.data,
    mark: { type: "geoshape", stroke: "black" },
    transform: chart.transform,
    encoding: {
      color: {
        field: extractedHeaders[1],
        type: "nominal",
        scale: { range: covidColors(extractedHeaders[1]) },
        sort: covidSort(extractedHeaders[1], chartMsg.data),
      },
      shape: { field: "geo", type: "geojson" },
    },
  };
  delete chart.mark;
  delete chart.transform;
  delete chart.encoding;
  delete chart.concat;
  chart.projection = { type: "albersUsa" };
  chart.layer = [
    {
      data: {
        url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
        format: {
          type: "topojson",
          feature: "states",
        },
      },
      mark: {
        type: "geoshape",
        fill: "lightgray",
        stroke: "white",
      },
    },
    obj,
  ];

  chart = createTitle(chart, extractedHeaders, "map", extractedFilteredValues);
  return chart;
};
