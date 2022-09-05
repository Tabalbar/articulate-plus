/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const createChartTemplate = require("./createChartTemplate");
const findType = require("./helpers/findType");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
const covidColors = require("./covidHelpers/covidColors");
const covidSort = require("./covidHelpers/covidSort");
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
  chart.mark = "bar";
  chart.encoding.x = {
    field: extractedHeaders[1],
    type: findType(extractedHeaders[1], chartMsg.data),
    axis: {
      labelFontSize: 15,
      titleFontSize: 15,
      labelLimit: 2000,
      labelAngle: -50,
    },
    sort: options.useCovidDataset
      ? covidSort(extractedHeaders[1], chartMsg.data)
      : [],
  };
  chart.encoding.y = {
    aggregate: "sum",
    field: extractedHeaders[0],
    axis: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
    type: findType(extractedHeaders[0], chartMsg.data),
  };

  chart.encoding.color = {
    field: extractedHeaders[1],
    type: findType(extractedHeaders[1], chartMsg.data),
    scale: options.useCovidDataset
      ? {
          range: covidColors(extractedHeaders[1]),
        }
      : {},
    legend: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
    sort: options.useCovidDataset
      ? covidSort(extractedHeaders[1], chartMsg.data)
      : [],
  };

  chart = createTitle(chart, extractedHeaders, "bar", extractedFilteredValues);
  chart = createTransform(chart, chartMsg, extractedFilteredValues);
  // chart.transform.push({
  //   type: "aggregate",
  //   groupby: ["x"],
  //   fields: [extractedHeaders[1]],
  //   ops: ["distinct"],
  // });
  return chart;
};
