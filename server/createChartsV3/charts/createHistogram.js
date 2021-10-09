const createTitle = require("./helpers/specifications/createTitle");
const findType = require("./helpers/findType");
const covidColors = require("./covidHelpers/covidColors");
const covidSort = require("./covidHelpers/covidSort");
const createTransform = require("./helpers/specifications/createTransform");
const createChartTemplate = require("./createChartTemplate");

module.exports = (
  chartMsg,
  extractedHeader,
  extractedFilteredValues,
  headerFrequencyCount
) => {
  let chart = createChartTemplate(chartMsg, headerFrequencyCount);
  chart.mark = "bar";
  chart.encoding.x = {
    field: extractedHeader,
    type: findType(extractedHeader, chartMsg.data),
    axis: { labelAngle: -50, grid: false },
    sort: covidSort(extractedHeader, chartMsg.data),
  };
  chart.encoding.color = {
    field: extractedHeader,
    type: findType(extractedHeader, chartMsg.data),
    scale: {
      range: covidColors(extractedHeader),
    },
    sort: covidSort(extractedHeader, chartMsg.data),
  };
  chart.encoding.y = {
    aggregate: "count",
    title: "Number of Counties",
  };
  chart = createTitle(chart, [extractedHeader], "bar", extractedFilteredValues);
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  return chart;
};
