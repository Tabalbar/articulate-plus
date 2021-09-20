module.exports = (
  chartObj,
  extractedHeaders,
  filteredHeaders,
  headerFrequencyCount
) => {
  let charts = [];
  switch (intent) {
    case "line":
      if (extractedHeaders.length == 2) {
        let chart = run(
          chartObj.intent,
          extractedHeaders,
          chartObj.data,
          headerFrequencyCount,
          chartObj.command,
          chartObj.options,
          filteredHeaders
        );
        charts.push(chart);
      } else if (extractedHeaders.length >= 3) {
        {
          for (let i = 2; i < extractedHeaders.length; i++) {
            let threeExtractedHeaders = [
              extractedHeaders[0],
              extractedHeaders[1],
              extractedHeaders[i],
            ];
            let chart = run(
              intent,
              threeExtractedHeaders,
              chartMsg.data,
              headerFrequencyCount,
              chartMsg.command,
              chartMsg.options,
              filteredHeaders
            );
            charts.push(chart);
          }
        }
      } else {
        charts.push("");
      }
      break;
    case "map":
      if (extractedHeaders.length >= 2) {
        for (let i = 0; i < extractedHeaders.length; i++) {
          let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[i]];
          let chart = run(
            intent,
            twoExtractedHeaders,
            chartMsg.data,
            headerFrequencyCount,
            chartMsg.command,
            chartMsg.options,
            filteredHeaders
          );
          charts.push(chart);
        }
      } else {
        charts.push("");
      }
      break;
    case "heatmap":
      if (extractedHeaders.length >= 2) {
        for (let i = 0; i < extractedHeaders.length; i++) {
          let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[i]];
          let chart = run(
            intent,
            twoExtractedHeaders,
            chartMsg.data,
            headerFrequencyCount,
            chartMsg.command,
            chartMsg.options,
            filteredHeaders
          );
          charts.push(chart);
        }
      } else {
        charts.push("");
      }
      break;
    case "bar":
      if (extractedHeaders.length == 1) {
        let chart = run(
          intent,
          extractedHeaders,
          chartMsg.data,
          headerFrequencyCount,
          chartMsg.command,
          chartMsg.options,
          filteredHeaders
        );
        charts.push(chart);
      } else {
        for (let i = 0; i < extractedHeaders.length; i++) {
          let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[i]];
          let chart = run(
            intent,
            twoExtractedHeaders,
            chartMsg.data,
            headerFrequencyCount,
            chartMsg.command,
            chartMsg.options,
            filteredHeaders
          );
          charts.push(chart);
        }
      }
      break;
  }
  return charts;
};
