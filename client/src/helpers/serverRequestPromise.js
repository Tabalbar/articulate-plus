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
export async function serverRequestPromise(
  chartMsg,
  setChartMsg,
  modifiedChartOptions,
  setVoiceMsg,
  charts,
  setCharts
) {
  return new Promise((resolve, reject) => {
    //Check charts to pivot
    let pivotTheseCharts = [];
    for (let i = 0; i < charts.length; i++) {
      if (charts[i].pivotThis) {
        pivotTheseCharts.push(charts[i]);
      }
    }
    let selectedCharts = [];
    for (let i = 0; i < charts.length; i++) {
      if (charts[i].visible) {
        selectedCharts.push(charts[i]);
      }
    }
    //API request
    fetch("/createCharts", {
      method: "POST",
      body: JSON.stringify({
        chartMsg,
        modifiedChartOptions,
        pivotTheseCharts,
        selectedCharts,
      }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((res) => res.text())
      .then((data) => {
        resolve(data);
      });
  });
}
