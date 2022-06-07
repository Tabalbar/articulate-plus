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

module.exports = (pythonResponse, chartMsg) => {
  if (pythonResponse == null) {
    console.log("pythonResponse is null");
    chartMsg.pythonCharts = [];

    return chartMsg;
  }
  const pythonChartMsg = JSON.parse(pythonResponse);
  if (!pythonChartMsg.hasOwnProperty("visualization_task")) {
    console.log("no vis task");
    chartMsg.pythonCharts = [];

    return chartMsg;
  }

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
    return chartMsg;
  }

  // let tmpData = [];
  // for (let i = 0; i < pythonChartMsg.data_query_results.length; i++) {
  //   let tmp = pythonChartMsg.data_query_results[i];
  //   tmp = tmp.replace("(", "");
  //   tmp = tmp.replace(")", "");
  //   tmp = tmp.replace(/'/g, "");
  //   tmp = tmp.replace('"', "");
  //   // tmp = tmp.replace(/-/g, " ");,/
  //   tmp = tmp.split(",");
  //   let tmpObj = {};
  //   console.log(tmp);
  //   for (let j = 0; j < tmp.length; j++) {
  //     tmp[j] = tmp[j].trim();
  //     let attribute = checkDataType(tmp[j], chartMsg);
  //     if (attribute === "map") {
  //     }
  //     tmpObj[attribute] = tmp[j];
  //   }
  //   tmpData.push(tmpObj);
  // }

  // chart = createTransform(
  //   chart,
  //   chartMsg,
  //   pythonChartMsg.visualization_task.filters
  // );

  // // let extractedHeaders = [];
  // // for (
  // //   let i = 0;
  // //   i < pythonChartMsg.visualization_task.horizontal_axis.length;
  // //   i++
  // // ) {
  // //   extractedHeaders.push(pythonChartMsg.visualization_task.horizontal_axis[i]);
  // // }
  // console.log(pythonChartMsg.visualization_task.horizontal_axis, "******");
  // const horizontal_axis = Object.keys(tmpData[0]);
  // console.log(horizontal_axis);

  // if (horizontal_axis.length === 0) {
  //   console.log("no horizontal axis given");
  //   return [];
  // }

  let plotType = pythonChartMsg.visualization_task.plot_type;
  let extractedHeaders = "";
  let filteredHeaders = "";
  let keys = Object.keys(pythonChartMsg.visualization_task.filters);

  for (let i = 0; i < keys.length; i++) {
    for (
      let j = 0;
      j < pythonChartMsg.visualization_task.filters[keys[i]].length;
      j++
    ) {
      filteredHeaders +=
        pythonChartMsg.visualization_task.filters[keys[i]][j] + " ";
    }
  }

  for (
    let i = 0;
    i < pythonChartMsg.visualization_task.horizontal_axis.length;
    i++
  ) {
    extractedHeaders +=
      pythonChartMsg.visualization_task.horizontal_axis[i] + " ";
  }
  switch (plotType) {
    case "bar chart":
      // chart = createBarChart(
      //   chart,
      //   chartMsg.pythonCharts.data,
      //   horizontal_axis,
      //   chartMsg
      // );
      plotType = "histogram";
      break;
    case "line chart":
      // chart = createLineChart(chart, data, filters, horizontal_axis, chartMsg);
      plotType = "line";
      break;
    case "tree map":
      // chart = createMap(chart, data, filters, horizontal_axis, chartMsg);
      plotType = "map";
      break;
    default:
      plotType = "histogram";
  }

  let command =
    "Show me a " + plotType + " of " + extractedHeaders + filteredHeaders;

  command = command.replace("_", " ");
  // chartMsg.pythonCharts = [chart];
  // chartMsg.pythonCharts.data = tmpData;
  return { plotType: plotType, command: command };
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

const createLineChart = (chart, data, filters, horizontalAxis, chartMsg) => {
  chart.mark = "line";
};

const createMap = (chart, data, filters, horizontalAxis, chartMsg) => {
  chart.mark = "map";
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

const createTransform = (chart, chartMsg, extractedFilteredValues) => {
  let accessors = [];
  // console.log(extractedFilteredValues);
  let keys = Object.keys(extractedFilteredValues);
  for (let i = 0; i < keys.length; i++) {
    if (extractedFilteredValues[keys[i]].length > 0) {
      if (findType(keys[i], chartMsg.data) === "nominal") {
        // console.log({
        //   field: keys[i],
        //   oneOf: extractedFilteredValues[keys[i]],
        // });
        chart.transform.push({
          filter: { field: keys[i], oneOf: extractedFilteredValues[keys[i]] },
        });
      }
      // else if (findType(keys[i], chartMsg.data) === "temporal") {
      //   chart.transform.push({
      //     filter: {
      //       timeUnit: "year",
      //       field: keys[i],
      //       range: [
      //         extractedFilteredValues[keys[i]][0],
      //         extractedFilteredValues[keys[i]][1],
      //       ],
      //     },
      //   });
      // }
    }
  }

  return chart;
};
