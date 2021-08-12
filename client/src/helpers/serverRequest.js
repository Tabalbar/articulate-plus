import UseVoice from "../components/voice/UseVoice";

export async function serverRequest(
  chartMsg,
  setChartMsg,
  modifiedChartOptions,
  mute,
  setClippyImage,
  thinkingImage,
  setVoiceMsg
) {
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
  const body = await response.text();

  // console.log(JSON.parse(body.chartMsg))
  const responseChartMsg = JSON.parse(body);
  let tmpChartMsg = responseChartMsg.chartMsg;
  let newCharts = [
    ...tmpChartMsg.explicitChart,
    ...tmpChartMsg.inferredChart,
    ...tmpChartMsg.modifiedChart,
  ];
  newCharts = newCharts.filter((x) => {
    return x !== "";
  });
  setChartMsg((prev) => {
    return {
      ...prev,
      charts: [...prev.charts, ...newCharts],
      headerFrequencyCount:
        tmpChartMsg.headerFrequencyCount.headerFrequencyCount,
    };
  });
  let count = newCharts.length;
  let assistantResponse;

  console.log(newCharts[0]);
  if (count == 0) {
    assistantResponse = "I couldn't find any charts for you";
  } else {
    assistantResponse = "I have " + count.toString() + " charts for you.";
    assistantResponse += " I have a " + newCharts[0].charts.spec.title + "...";

    for (let i = 1; i < newCharts.length - 1; i++) {
      assistantResponse += newCharts[i].charts.spec.title + "...";
    }
    if (newCharts.length > 1) {
      assistantResponse +=
        " and a " + newCharts[newCharts.length - 1].charts.spec.title;
    }
  }
  let msg = UseVoice(assistantResponse, mute);
  setVoiceMsg(assistantResponse);
  return;
}
