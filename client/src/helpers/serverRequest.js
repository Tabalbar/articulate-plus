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
  mute,
  setVoiceMsg
) {
  //API request
  const response = await fetch("/createCharts", {
    method: "POST",
    body: JSON.stringify({
      chartMsg,
      modifiedChartOptions,
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
    ...tmpChartMsg.explicitChart,
    ...tmpChartMsg.inferredChart,
    ...tmpChartMsg.modifiedChart,
  ];
  //Clean up for charts that weren't generated
  newCharts = newCharts.filter((x) => {
    return x !== "";
  });
  console.log(tmpChartMsg.window_semantic);
  //Put new charts into state
  setChartMsg((prev) => {
    return {
      ...prev,
      charts: [...prev.charts, ...newCharts],
      window_semantic: tmpChartMsg.window_semantic,
      window: tmpChartMsg.window,
    };
  });

  // How many charts were genderated
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
