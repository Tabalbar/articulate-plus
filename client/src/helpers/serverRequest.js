import UseVoice from "../components/voice/UseVoice";

export async function serverRequest(
  chartMsg,
  setChartMsg,
  withClippy,
  modifiedChartOptions,
  mute
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

  setChartMsg((prev) => {
    return {
      ...prev,
      charts: [
        ...prev.charts,
        tmpChartMsg.explicitChart,
        tmpChartMsg.inferredChart,
        tmpChartMsg.modifiedChart,
      ],
      headerFrequencyCount:
        tmpChartMsg.headerFrequencyCount.headerFrequencyCount,
    };
  });

  let count = 0;
  if (tmpChartMsg.explicitChart !== "") {
    count++;
  }
  if (tmpChartMsg.inferredChart !== "") {
    count++;
  }
  if (tmpChartMsg.modifiedChart !== "") {
    count++;
  }
  let assistantResponse = "";

  if (count == 0) {
    assistantResponse = "I couldn't find any charts for you";
  } else {
    assistantResponse = "I have " + count.toString() + " charts for you.";
    if (tmpChartMsg.explicitChart !== "") {
      assistantResponse +=
        " I have a " + tmpChartMsg.explicitChart.charts.spec.title + "...";
    }
    if (tmpChartMsg.inferredChart !== "") {
      if (assistantResponse.substring(assistantResponse.length - 3) == "...") {
        assistantResponse +=
          " Then I have a " +
          tmpChartMsg.inferredChart.charts.spec.title +
          "...";
      } else {
        assistantResponse +=
          " I have a " + tmpChartMsg.inferredChart.charts.spec.title + "...";
      }
    }
    if (tmpChartMsg.modifiedChart !== "") {
      if (assistantResponse.substring(assistantResponse.length - 3) == "...") {
        assistantResponse +=
          " Then I have a " +
          tmpChartMsg.modifiedChart.charts.spec.title +
          "...";
      } else {
        assistantResponse +=
          " I have a " + tmpChartMsg.modifiedChart.charts.spec.title + ".";
      }
    }
  }
  withClippy((clippy) => clippy.speak(assistantResponse));
  let msg = UseVoice(assistantResponse, mute);

  return msg;
}
