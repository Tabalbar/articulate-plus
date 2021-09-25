module.exports = (extractedHeaders, intent, filteredHeaders) => {
  let chartTitle = "";
  let headerLength = extractedHeaders.length;
  let headerTitles = [];
  let filteredHeaderLength = 0;
  let keys = Object.keys(filteredHeaders);
  for (let i = 0; i < keys.length; i++) {
    if (filteredHeaders[keys[i]].length > 0) {
      filteredHeaderLength++;
    }
  }

  let filteredHeaderTitles = [];

  if (headerLength > 3) {
    headerLength = 3;
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    let headers = extractedHeaders[i].split(" ");
    let title = "";
    for (let n = 0; n < headers.length; n++) {
      title += headers[n].charAt(0).toUpperCase() + headers[n].slice(1) + " ";
    }
    headerTitles.push(title);
  }
  for (let i = 0; i < keys.length; i++) {
    for (let j = 0; j < filteredHeaders[keys[i]].length; j++) {
      let headers = filteredHeaders[keys[i]][j].split(" ");
      let title = "";
      for (let n = 0; n < headers.length; n++) {
        title += headers[n].charAt(0).toUpperCase() + headers[n].slice(1) + " ";
      }
      filteredHeaderTitles.push(title);
    }
  }
  for (let i = 0; i < filteredHeaders.length; i++) {
    for (let j = 0; j < filteredHeaders[i].length; j++) {}
  }
  if (intent == "map") {
    chartTitle = "Map of " + extractedHeaders[1];
  } else {
    switch (headerLength) {
      case 1:
        switch (intent) {
          case "bar":
            chartTitle += "Histogram of " + headerTitles[0];
            break;
          case "line":
            chartTitle += "Line chart of " + headerTitles[0];
            break;
          case "scatter":
            chartTitle += "Scatter plot of " + extractedHeaders[0];
            break;
        }
        break;
      case 2:
        if (intent == "bar") {
          chartTitle +=
            "Heatmap Sum of " + headerTitles[1] + "vs. " + headerTitles[0];
        } else {
          chartTitle +=
            intent.charAt(0).toUpperCase() +
            intent.slice(1) +
            " Chart of " +
            headerTitles[1] +
            " vs. " +
            headerTitles[0];
        }

        break;

      case 3:
        chartTitle +=
          intent.charAt(0).toUpperCase() +
          intent.slice(1) +
          " Chart of " +
          headerTitles[1] +
          " vs. " +
          headerTitles[0] +
          "Colored by " +
          headerTitles[2];
        break;
      default:
        return "";
    }
  }
  if (filteredHeaderLength > 0) {
    chartTitle += " Filtered by ";
    for (let i = 0; i < filteredHeaderTitles.length; i++) {
      if (i == filteredHeaderTitles.length - 1) {
        chartTitle += filteredHeaderTitles[i];
        break;
      }
      chartTitle += filteredHeaderTitles[i] + " and ";
    }
  }

  return chartTitle;
};
