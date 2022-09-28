/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const createChartTemplate = require("../createChartsV3/charts/createChartTemplate");
const findType = require("../createChartsV3/charts/helpers/findType");
const covidColors = require("../createChartsV3/charts/covidHelpers/covidColors");
const covidSort = require("../createChartsV3/charts/covidHelpers/covidSort");
const createHeatmap = require("../createChartsV3/charts/createHeatmap");
const removeOtherTypes = require("../createChartsV3/charts/helpers/removeOtherTypes");
const switchHeaders = require("../createChartsV3/charts/helpers/switchHeaders");
const createLine = require("../createChartsV3/charts/createLine");
const createBar = require("../createChartsV3/charts/createBar");
const createMap = require("../createChartsV3/charts/createMap");

module.exports = (pythonResponse, chartMsg) => {
  let options = {
    useCovidDataset: true,
    sentimentAnalysis: false,
    window: {
      toggle: false,
      pastSentences: 0,
    },
    neuralNetwork: false,
    useSynonyms: false,
    randomCharts: {
      toggle: false,
      minutes: 10,
    },
    threshold: 3,
    filter: {
      toggle: false,
      pastSentences: 0,
      threshold: 5,
    },
    pivotCharts: false,
  };
  if (pythonResponse == null) {
    console.log("pythonResponse is null");
    chartMsg.pythonCharts = [];

    return "none";
  }
  const pythonChartMsg = JSON.parse(pythonResponse);
  // if (!pythonChartMsg.hasOwnProperty("visualization_task")) {
  //   console.log("no vis task");
  //   chartMsg.pythonCharts = [];

  //   return chartMsg;
  // }

  let chart = createChartTemplate(chartMsg, {}, {});

  let createVis = false;
  for (let i = 0; i < pythonChartMsg.dialogue_act.length; i++) {
    if (
      pythonChartMsg.dialogue_act[i] === "createvis" ||
      pythonChartMsg.dialogue_act[i] === "modifyvis"
    ) {
      createVis = true;
      break;
    }
  }
  if (!createVis) {
    chartMsg.pythonCharts = [];
    console.log(pythonChartMsg.dialogue_act);
    console.log("Not classified as createvis or modifyvis");
    return "none";
  }

  let plotType = pythonChartMsg.visualization_task.plot_type;
  let filters = pythonChartMsg.visualization_task.filters;
  chartMsg.pythonData = pythonChartMsg.data_vega_lite_spec;
  let extractedHeaders = Object.keys(chartMsg.pythonData[0]);
  console.log(extractedHeaders);

  switch (plotType) {
    case "heat map":
      if (extractedHeaders[1] == "fips" || extractedHeaders[0] == "fips") {
        for (let i = 0; i < extractedHeaders.length; i++) {
          if (extractedHeaders[i] == "fips") {
            switchHeaders(extractedHeaders, 0, i);
          }
        }
        chart = createMap(
          chartMsg,
          extractedHeaders,
          filters,
          {},
          {},
          options,
          true,
          chartMsg.pythonData
        );
        console.log(chart, "*****");
      } else {
        for (let i = 0; i < extractedHeaders.length; i++) {
          if (extractedHeaders[i] == "NUM_COUNTIES") {
            switchHeaders(extractedHeaders, 2, i);
          }
        }
        console.log(extractedHeaders);
        chart = createHeatmap(
          chartMsg,
          extractedHeaders,
          filters,
          {},
          {},
          options,
          true
        );
      }

      break;
    case "line":
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == "date") {
          switchHeaders(extractedHeaders, 0, i);
        }
      }
      for (let i = 1; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == "NUM_CASES") {
          switchHeaders(extractedHeaders, 1, i);
        }
      }
      chart = createLine(
        chartMsg,
        extractedHeaders,
        filters,
        {},
        {},
        options,
        true
      );
      break;
    case "bar chart":
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == "NUM_COUNTIES") {
          switchHeaders(extractedHeaders, 0, i);
        }
      }

      chart = createBar(
        chartMsg,
        extractedHeaders,
        filters,
        {},
        {},
        options,
        true
      );
      // chart = createMap(chart, data, filters, horizontal_axis, chartMsg);
      break;
    default:
      plotType = "histogram";
  }
  chart.pythonData = chartMsg.pythonData;
  chart.filters = createTransform(chartMsg, filters);
  return chart;
};

// chart.encoding.x = {
//   field: extractedHeader,
//   type: findType(extractedHeader, chartMsg.data),
//   axis: { labelAngle: -50, grid: false },
//   sort: covidSort(extractedHeader, chartMsg.data),
// };
// chart.encoding.color = {
//   field: extractedHeader,
//   type: findType(extractedHeader, chartMsg.data),
//   scale: {
//     range: covidColors(extractedHeader),
//   },
//   sort: covidSort(extractedHeader, chartMsg.data),
// };
// chart.encoding.y = {
//   aggregate: "count",
// };
// chart = createTitle(chart, [extractedHeader], "bar", extractedFilteredValues);
// chart = createTransform(chart, chartMsg, extractedFilteredValues);

const createBarChart = (chart, data, horizontalAxis, chartMsg) => {
  chart.mark = "bar";
  chart.encoding.x = {
    field: horizontalAxis[0],
    type: findType(horizontalAxis[0], chartMsg.data),
    axis: { grid: false, labelAngle: -50 },
  };
  chart.encoding.color = {
    field: horizontalAxis[1],
    type: findType(horizontalAxis[0], chartMsg.data),
    scale: {
      range: covidColors(horizontalAxis[0]),
    },
    sort: covidSort(horizontalAxis[0], chartMsg.data),
  };
  chart.encoding.y = {
    field: horizontalAxis[1],
    type: "quantitative",
  };
  return chart;
};

// createTransform = (filters) => {};

const checkDataType = (dataPoint, chartMsg) => {
  let attribute = "count";
  for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    for (let j = 0; j < chartMsg.featureMatrix[i].length; j++) {
      if (chartMsg.featureMatrix[i][j] === dataPoint) {
        attribute = chartMsg.featureMatrix[i][0];
        break;
      }
    }
    if (attribute !== "count") {
      break;
    }
  }
  if (dataPoint.includes(".")) {
    attribute = "lat";
  }
  return attribute;
};

const createTransform = (chartMsg, extractedFilteredValues) => {
  let accessors = [];
  let filters = [];
  // console.log(extractedFilteredValues);
  let keys = Object.keys(extractedFilteredValues);
  for (let i = 0; i < keys.length; i++) {
    if (extractedFilteredValues[keys[i]].length > 0) {
      if (findType(keys[i], chartMsg.data) === "nominal") {
        filters.push({
          filter: { field: keys[i], oneOf: extractedFilteredValues[keys[i]] },
        });
      }
    }
  }
  return filters;
};
