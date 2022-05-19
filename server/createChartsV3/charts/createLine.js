const findType = require("./helpers/findType");
const covidColors = require("./covidHelpers/covidColors");
const covidSort = require("./covidHelpers/covidSort");
const createChartTemplate = require("./createChartTemplate");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");

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
  console.log(chart.filterFrequencyCount);
  chart.mark = {
    type: "line",
    point: { size: 100 },
  };
  switch (extractedHeaders.length) {
    case 2:
      chart.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], chartMsg.data),
        axis: {
          grid: false,
          labelAngle: -50,
          labelFontSize: 10,
          titleFontSize: 10,
        },
      };
      chart.encoding.y = {
        field: extractedHeaders[1],
        axis: { labelFontSize: 10, titleFontSize: 10 },
        type: findType(extractedHeaders[1], chartMsg.data),
        aggregate: "sum",
      };
      break;
    case 3:
      chart.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], chartMsg.data),
        axis: {
          labelAngle: -50,
          title: "",
          labelFontSize: 15,
          titleFontSize: 15,
          format: "%x",
        },
        sort: options.useCovidDataset
          ? covidSort(extractedHeaders[0], chartMsg.data)
          : [],
        // axis: { grid: false },
      };
      chart.encoding.y = {
        aggregate: "sum",
        axis: { labelFontSize: 10, titleFontSize: 10 },
        field: extractedHeaders[1],
      };
      chart.encoding.color = {
        field: extractedHeaders[2],
        type: findType(extractedHeaders[2], chartMsg.data),
        legend: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
        scale: options.useCovidDataset
          ? {
              range: options.useCovidDataset
                ? covidColors(extractedHeaders[2])
                : [],
            }
          : {},
        sort: options.useCovidDataset
          ? covidSort(extractedHeaders[2], chartMsg.data)
          : [],
      };
      break;
  }
  chart = createTitle(chart, extractedHeaders, "line", extractedFilteredValues);
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  return chart;
};
