const covidSort = require("./covidHelpers/covidSort");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
const findType = require("./helpers/findType");
const createChartTemplate = require("./createChartTemplate");

module.exports = (
  chartMsg,
  extractedHeaders,
  extractedFilteredValues,
  headerFrequencyCount
) => {
  let chart = createChartTemplate(chartMsg, headerFrequencyCount);
  chart.mark = "rect";
  chart.encoding.x = {
    field: extractedHeaders[0],
    type: findType(extractedHeaders[0], chartMsg.data),
    axis: { labelAngle: -50, grid: false },
    sort: covidSort(extractedHeaders[0], chartMsg.data),
  };
  chart.encoding.y = {
    field: extractedHeaders[1],
    type: findType(extractedHeaders[1], chartMsg.data),
    sort: covidSort(extractedHeaders[1], chartMsg.data),
  };
  chart.encoding.color = {
    type: "quantitative",
    aggregate: "count",
    scale: { scheme: "reds" },
  };
  chart.config = {
    axis: { ticks: false, labelPadding: 10, domain: false },
    view: { strokeWidth: 0 },
  };
  chart = createTitle(
    chart,
    extractedHeaders,
    "heatmap",
    extractedFilteredValues
  );
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  return chart;
};
