module.exports = (chartMsg) => {
  for (let i = 0; i < chartMsg.explicitChart.length; i++) {
    if (chartMsg.explicitChart[i] !== "") {
      chartMsg.explicitChart[i].charts.spec.chartSelection = "explicit";

      for (let j = 0; j < chartMsg.inferredChart.length; j++) {
        if (
          isChartsEqual(chartMsg.explicitChart[i], chartMsg.inferredChart[j])
        ) {
          chartMsg.inferredChart[j] = "";
          chartMsg.explicitChart[i].charts.spec.chartSelection +=
            " window+sentiment";
        }
      }

      for (let n = 0; n < chartMsg.modifiedChart.length; n++) {
        if (
          isChartsEqual(chartMsg.explicitChart[i], chartMsg.modifiedChart[n]) &&
          chartMsg.explicitChart[i] !== ""
        ) {
          chartMsg.modifiedChart[n] = "";
          chartMsg.explicitChart[i].charts.spec.chartSelection += " window";
        }
      }
    }
  }

  for (let i = 0; i < chartMsg.inferredChart.length; i++) {
    if (chartMsg.inferredChart[i] !== "") {
      chartMsg.inferredChart[i].charts.spec.chartSelection = "window+sentiment";

      for (let j = 0; j < chartMsg.modifiedChart.length; j++) {
        if (
          isChartsEqual(chartMsg.inferredChart[i], chartMsg.modifiedChart[j]) &&
          chartMsg.explicitChart[i] !== ""
        ) {
          chartMsg.modifiedChart[j] = "";
          chartMsg.explicitChart[i].charts.spec.chartSelection += " window";
        }
      }
    }
  }

  for (let i = 0; i < chartMsg.modifiedChart.length; i++) {
    if (chartMsg.modifiedChart[i] !== "") {
      chartMsg.modifiedChart[i].charts.spec.chartSelection = "window";
    }
  }
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
