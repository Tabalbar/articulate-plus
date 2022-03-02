const createChartTemplate = require("../createChartsV3/charts/createChartTemplate");
const findType = require("../createChartsV3/charts/helpers/findType");
const covidColors = require("../createChartsV3/charts/covidHelpers/covidColors");
const covidSort = require("../createChartsV3/charts/covidHelpers/covidSort");

module.exports = (pythonResponse, chartMsg) => {
  if (pythonResponse == null) {
    console.log("pythonResponse is null");
    return;
  }
  const pythonChartMsg = JSON.parse(pythonResponse);
  if (!pythonChartMsg.hasOwnProperty("visualization_task")) {
    console.log("no vis task");
    return;
  }

  let chart = createChartTemplate(chartMsg, {}, {});

  let createVis = false;
  for (let i = 0; i < pythonChartMsg.dialogue_act.length; i++) {
    console.log(pythonChartMsg.dialogue_act[i]);
    if (
      pythonChartMsg.dialogue_act[i] === "createVis" ||
      pythonChartMsg.dialogue_act[i] === "modifyvis"
    ) {
      createVis = true;
      break;
    }
  }
  if (!createVis) {
    return [];
  }

  let tmpData = [];
  for (let i = 0; i < pythonChartMsg.data_query_results.length; i++) {
    let tmp = pythonChartMsg.data_query_results[i];
    tmp = tmp.replace("(", "");
    tmp = tmp.replace(")", "");
    tmp = tmp.replace(/'/g, "");
    tmp = tmp.replace('"', "");
    // tmp = tmp.replace(/-/g, " ");,/
    tmp = tmp.split(",");
    let tmpObj = {};
    console.log(tmp);
    for (let j = 0; j < tmp.length; j++) {
      tmp[j] = tmp[j].trim();
      let attribute = checkDataType(tmp[j], chartMsg);
      if (attribute === "map") {
      }
      tmpObj[attribute] = tmp[j];
    }
    tmpData.push(tmpObj);
  }
  chartMsg.pythonCharts.data = tmpData;

  chart = createTransform(
    chart,
    chartMsg,
    pythonChartMsg.visualization_task.filters
  );

  // let extractedHeaders = [];
  // for (
  //   let i = 0;
  //   i < pythonChartMsg.visualization_task.horizontal_axis.length;
  //   i++
  // ) {
  //   extractedHeaders.push(pythonChartMsg.visualization_task.horizontal_axis[i]);
  // }
  console.log(pythonChartMsg.visualization_task.horizontal_axis, "******");
  const horizontal_axis = Object.keys(chartMsg.pythonCharts.data[0]);
  console.log(horizontal_axis);

  if (horizontal_axis.length === 0) {
    console.log("no horizontal axis given");
    return [];
  }

  const plot_type = pythonChartMsg.visualization_task.plot_type;
  switch (plot_type) {
    case "bar chart":
      chart = createBarChart(
        chart,
        chartMsg.pythonCharts.data,
        horizontal_axis,
        chartMsg
      );
    // case "line chart":
    //   chart = createLineChart(chart, data, filters, horizontal_axis, chartMsg);
    // case "tree map":
    //   chart = createMap(chart, data, filters, horizontal_axis, chartMsg);
    default:
      chart = createBarChart(
        chart,
        chartMsg.pythonCharts.data,
        horizontal_axis,
        chartMsg
      );
  }
  chartMsg.pythonCharts = chart;
  return chartMsg;
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
    field: horizontalAxis[0],
    type: findType(horizontalAxis[0], chartMsg.data),
    scale: {
      range: covidColors(horizontalAxis),
    },
    sort: covidSort(horizontalAxis[0], chartMsg.data),
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
