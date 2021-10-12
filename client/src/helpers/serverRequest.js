/**
 * API request to Node Server for chart generation
 *
 * @param {object} chartMsg message for server
 * @param {function} setChartMsg set state for server request
 * @param {object} modifiedChartOptions Handler for toggling algorithm
 * @param {boolean} mute To speak or not to speak voice synthesizer
 * @param {function} setVoiceMsg set state for voice synthesizer
 * @returns
 */
export async function serverRequest(
  chartMsg,
  setChartMsg,
  modifiedChartOptions,
  setVoiceMsg,
  charts,
  setCharts
) {
  //Check charts to pivot
  let pivotTheseCharts = [];
  for (let i = 0; i < charts.length; i++) {
    if (charts[i].pivotThis) {
      pivotTheseCharts.push(charts[i]);
    }
  }

  //API request
  const response = await fetch("/createCharts", {
    method: "POST",
    body: JSON.stringify({
      chartMsg,
      modifiedChartOptions,
      pivotTheseCharts,
    }),
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });
  // decrypt message from server
  const body = await response.text();
  const responseChartMsg = JSON.parse(body);

  //tmp var to hold charts
  let tmpChartMsg = responseChartMsg.chartMsg;
  //Must add explicit first
  let newCharts = [
    ...tmpChartMsg.randomCharts,
    ...tmpChartMsg.explicitChart,
    ...tmpChartMsg.mainAI,
    ...tmpChartMsg.mainAIOverhearing,
    ...tmpChartMsg.pivotChart,
  ];
  //Clean up for charts that weren't generated
  newCharts = newCharts.filter((x) => {
    return x !== "";
  });

  //id on charts
  let startingId = chartMsg.charts.length;
  for (let i = 0; i < newCharts.length; i++) {
    newCharts[i].id = startingId + i;
  }

  //cleaning up for pivot
  let tmpCharts = chartMsg.charts;
  for (let i = 0; i < tmpCharts.length; i++) {
    tmpCharts[i].pivotThis = false;
  }

  //Put header frequency count into state
  setChartMsg((prev) => {
    return {
      ...prev,
      charts: [...tmpCharts, ...newCharts],
      mainAICount: tmpChartMsg.mainAICount,
      mainAIOverhearingCount: tmpChartMsg.mainAIOverhearingCount,
      total: tmpChartMsg.total,
    };
  });

  // How many charts were generated
  let count = newCharts.length;
  let assistantResponse;

  if (count == 0) {
    assistantResponse = "I couldn't find any charts for you";
  } else if (count == 1) {
    assistantResponse = "I have " + count.toString() + " chart for you.";
  } else {
    assistantResponse = "I have " + count.toString() + " charts for you.";
  }
  //Voice syntheiszer
  setVoiceMsg(assistantResponse);

  return;
}
