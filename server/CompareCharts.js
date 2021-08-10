module.exports = (chartMsg) => {
  for (let i = 0; i < chartMsg.charts.length; i++) {
    for (let j = 0; j < chartMsg.explicitChart.length; j++) {
      if (isChartsEqual(chartMsg.explicitChart[j], chartMsg.charts[i])) {
        chartMsg.explicitChart[j] = "";
        break;
      }
    }
  }
  for (let i = 0; i < chartMsg.charts.length; i++) {
    for (let j = 0; j < chartMsg.inferredChart.length; j++) {
      if (isChartsEqual(chartMsg.inferredChart[j], chartMsg.charts[i])) {
        chartMsg.inferredChart[j] = "";
        break;
      }
    }
  }
  for (let i = 0; i < chartMsg.charts.length; i++) {
    for (let j = 0; j < chartMsg.modifiedChart.length; j++) {
      if (isChartsEqual(chartMsg.modifiedChart[j], chartMsg.charts[i])) {
        chartMsg.modifiedChart[j] = "";
        break;
      }
    }
  }

  //Check if Explicit equal inferred and modified
  for (let i = 0; i < chartMsg.explicitChart.length; i++) {
    for (let j = 0; j < chartMsg.inferredChart.length; j++) {
      if (
        isChartsEqual(chartMsg.explicitChart[i], chartMsg.inferredChart[j]) &&
        chartMsg.explicitChart[i] !== ""
      ) {
        console.log("called");
        chartMsg.inferredChart[j] = "";
        chartMsg.explicitChart[i].charts.spec.chartSelection =
          "Explicit Window";
      }
    }
    for (let j = 0; j < chartMsg.modifiedChart.length; j++) {
      if (
        isChartsEqual(chartMsg.explicitChart[i], chartMsg.modifiedChart[j]) &&
        chartMsg.explicitChart[i] !== ""
      ) {
        chartMsg.modifiedChart[j] = "";
        chartMsg.explicitChart[i].charts.spec.chartSelection += " Modified";
      }
    }
  }
  for (let i = 0; i < chartMsg.inferredChart.length; i++) {
    for (let j = 0; j < chartMsg.modifiedChart.length; j++) {
      if (
        isChartsEqual(chartMsg.inferredChart[i], chartMsg.modifiedChart[j]) &&
        chartMsg.inferredChart[i] !== ""
      ) {
        chartMsg.modifiedChart[j] = "";
        chartMsg.inferredChart[i].charts.spec.chartSelection =
          "Window Modified";
      }
    }
  }
  //   if (
  //     isChartsEqual(chartMsg.explicitChart, chartMsg.inferredChart) &&
  //     isChartsEqual(chartMsg.explicitChart, chartMsg.modifiedChart) &&
  //     chartMsg.explicitChart !== ""
  //   ) {
  //     chartMsg.inferredChart = "";
  //     chartMsg.modifiedChart = "";
  //     chartMsg.explicitChart.charts.spec.chartSelection =
  //       "Explicit and Window and Modifed";
  //   } else if (
  //     isChartsEqual(chartMsg.explicitChart, chartMsg.inferredChart) &&
  //     chartMsg.explicitChart !== ""
  //   ) {
  //     chartMsg.inferredChart = "";
  //     chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Window";
  //   } else if (
  //     isChartsEqual(chartMsg.explicitChart, chartMsg.modifiedChart) &&
  //     chartMsg.explicitChart !== ""
  //   ) {
  //     chartMsg.inferredChart = "";
  //     chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Modified";
  //   } else
  //   if (
  //     isChartsEqual(chartMsg.inferredChart, chartMsg.modifiedChart) &&
  //     chartMsg.inferredChart !== ""
  //   ) {
  //     chartMsg.modifiedChart = "";
  //     chartMsg.inferredChart.charts.spec.chartSelection = "Window and Modified";
  //   }
};

function isChartsEqual(chartOne, chartTwo) {
  if (chartOne == "" && chartTwo == "") {
    return true;
  }
  if (chartOne == "" && chartTwo !== "") {
    return false;
  }
  if (chartOne !== "" && chartTwo == "") {
    return false;
  }
  chartOne = chartOne.charts.spec;
  chartTwo = chartTwo.charts.spec;

  if (
    JSON.stringify(chartOne.encoding) == JSON.stringify(chartTwo.encoding) &&
    JSON.stringify(chartOne.mark) == JSON.stringify(chartTwo.mark) &&
    JSON.stringify(chartOne.transform) == JSON.stringify(chartTwo.transform) &&
    JSON.stringify(chartOne.layer) == JSON.stringify(chartTwo.layer)
  ) {
    return true;
  } else {
    return false;
  }
}
