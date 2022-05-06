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
  headerFrequencyCount,
  filterFrequencyCount,
  options
) => {
  let chart = createChartTemplate(
    chartMsg,
    headerFrequencyCount,
    filterFrequencyCount
  );
  chart.mark = "bar";
  chart.encoding.x = {
    field: extractedHeader,
    type: findType(extractedHeader, chartMsg.data),
    axis: { labelAngle: -50, labelFontSize: 10, titleFontSize: 10 },
    sort: options.useCovidDataset
      ? covidSort(extractedHeader, chartMsg.data)
      : [],
  };
  chart.encoding.color = {
    field: extractedHeader,
    type: findType(extractedHeader, chartMsg.data),
    scale: {
      range: covidColors(extractedHeader),
    },
    axis: { labelFontSize: 10, titleFontSize: 10 },
    sort: options.useCovidDataset
      ? covidSort(extractedHeader, chartMsg.data)
      : [],
  };
  chart.encoding.y = {
    aggregate: "count",
    legend: { labelFontSize: 10, titleFontSize: 10 },
  };
  chart = createTitle(chart, [extractedHeader], "bar", extractedFilteredValues);
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  // chart.transform.push({
  //   type: "aggregate",
  //   fields: [extractedHeader],
  //   ops: ["distinct"],
  // });
  return chart;
};
