module.exports = (chartMsg) => {
  for (let i = 0; i < chartMsg.explicitChart.length; i++) {
    if (chartMsg.explicitChart[i] !== "") {
      chartMsg.explicitChart[i].chartSelection = "explicit_point";

      for (let j = 0; j < chartMsg.mainAI.length; j++) {
        if (isChartsEqual(chartMsg.explicitChart[i], chartMsg.mainAI[j])) {
          chartMsg.mainAI[j] = "";
          chartMsg.explicitChart[i].chartSelection += " mainAI_point";
        }
      }

      for (let n = 0; n < chartMsg.mainAIOverhearing.length; n++) {
        if (
          isChartsEqual(
            chartMsg.explicitChart[i],
            chartMsg.mainAIOverhearing[n]
          ) &&
          chartMsg.explicitChart[i] !== ""
        ) {
          chartMsg.mainAIOverhearing[n] = "";
          chartMsg.explicitChart[i].chartSelection +=
            " mainAIOverhearing_point";
        }
      }
    }
  }

  for (let i = 0; i < chartMsg.mainAI.length; i++) {
    if (chartMsg.mainAI[i] !== "") {
      chartMsg.mainAI[i].chartSelection = "mainAI_point";

      for (let j = 0; j < chartMsg.mainAIOverhearing.length; j++) {
        if (
          isChartsEqual(chartMsg.mainAI[i], chartMsg.mainAIOverhearing[j]) &&
          chartMsg.explicitChart[i] !== ""
        ) {
          chartMsg.mainAIOverhearing[j] = "";
          chartMsg.mainAI[i].chartSelection += " mainAIOverhearing_point";
        }
      }
    }
  }

  for (let i = 0; i < chartMsg.mainAIOverhearing.length; i++) {
    if (chartMsg.mainAIOverhearing[i] !== "") {
      chartMsg.mainAIOverhearing[i].chartSelection = "mainAIOverhearing_point";
    }
  }

  for (let i = 0; i < chartMsg.pivotChart.length; i++) {
    for (let j = i + 1; j < chartMsg.pivotChart.length; j++) {
      if (isChartsEqual(chartMsg.pivotChart[i], chartMsg.pivotChart[j])) {
        chartMsg.pivotChart[j] = "";
        console.log(chartMsg.pivotChart[j]);
        break;
      }
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
  // chartOne = chartOne.charts.spec;
  // chartTwo = chartTwo.charts.spec;
  console.log(
    JSON.stringify(chartOne.encoding) == JSON.stringify(chartTwo.encoding)
  );
  console.log(JSON.stringify(chartOne.mark) == JSON.stringify(chartTwo.mark));
  console.log(
    JSON.stringify(chartOne.transform) == JSON.stringify(chartTwo.transform)
  );
  console.log(JSON.stringify(chartOne.layer) == JSON.stringify(chartTwo.layer));
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
