/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
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
  options,
  isPython
) => {
  let chart = createChartTemplate(
    chartMsg,
    headerFrequencyCount,
    filterFrequencyCount
  );
  chart.mark = { type: "line", point: true };
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
        type: "quantitative",
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
      if (isPython) {
        chart.encoding.y = {
          axis: { labelFontSize: 15, titleFontSize: 15 },
          field: extractedHeaders[1],
          type: "quantitative",
        };
      } else {
        chart.encoding.y = {
          axis: { labelFontSize: 15, titleFontSize: 15 },
          field: extractedHeaders[1],
        };
        chart = createTransform(chart, chartMsg, extractedFilteredValues);
      }

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
  return chart;
};
