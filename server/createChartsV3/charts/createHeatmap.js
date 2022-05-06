const covidSort = require("./covidHelpers/covidSort");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
const findType = require("./helpers/findType");
const createChartTemplate = require("./createChartTemplate");

module.exports = (
  chartMsg,
  extractedHeaders,
  extractedFilteredValues,
  headerFrequencyCount,
  filterFrequencyCount,
  options
) => {
  let chart = createChartTemplate(
    chartMsg,
    headerFrequencyCount,
    filterFrequencyCount
  );
  chart.mark = "rect";
  chart.encoding.x = {
    field: extractedHeaders[0],
    type: findType(extractedHeaders[0], chartMsg.data),
    axis: { labelAngle: -50, labelFontSize: 10, titleFontSize: 10 },
    sort: options.useCovidDataset
      ? covidSort(extractedHeaders[0], chartMsg.data)
      : [],
  };
  chart.encoding.y = {
    field: extractedHeaders[1],
    type: findType(extractedHeaders[1], chartMsg.data),
    sort: options.useCovidDataset
      ? covidSort(extractedHeaders[1], chartMsg.data)
      : [],
    axis: { labelFontSize: 10, titleFontSize: 10 },
  };
  chart.encoding.color = {
    type: "quantitative",
    aggregate: "count",
    scale: { scheme: "reds" },
    legend: { labelFontSize: 10, titleFontSize: 10 },
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
