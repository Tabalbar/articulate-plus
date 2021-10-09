const createChartTemplate = require("./createChartTemplate");
const findType = require("./helpers/findType");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
module.exports = (
  chartMsg,
  extractedHeaders,
  extractedFilteredValues,
  headerFrequencyCount
) => {
  let chart = createChartTemplate(chartMsg, headerFrequencyCount);
  chart.mark = "bar";
  chart.encoding.x = {
    field: extractedHeaders[1],
    type: findType(extractedHeaders[1], chartMsg.data),
    axis: { grid: false, labelAngle: -50 },
  };
  chart.encoding.y = {
    field: extractedHeaders[0],
    type: findType(extractedHeaders[0], chartMsg.data),
  };
  chart = createTitle(chart, extractedHeaders, "bar", extractedFilteredValues);
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  return chart;
};
