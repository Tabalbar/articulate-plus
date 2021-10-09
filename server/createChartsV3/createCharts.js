const countFilterFrequency = require("./overhearing/countFilterFrequency");
const countHeaderFrequency = require("./overhearing/countHeaderFrequency.js");
const createHistogram = require("./charts/createHistogram");
const extract = require("./extract");
const keepThis = require("./charts/helpers/keepThis");
const findAndRemoveOtherTypes = require("./charts/helpers/findAndRemoveOtherTypes");
const findTemporalAndQuantitative = require("./charts/helpers/findTemporalAndQuantitative");
const createLine = require("./charts/createLine");
const createMap = require("./charts/createMap");
const removeOtherTypes = require("./charts/helpers/removeOtherTypes");
const createHeatmap = require("./charts/createHeatmap");
const createBar = require("./charts/createBar");

module.exports = (intent, chartMsg, options) => {
  //Varaibles that holds the count for overheadering
  const headerFrequencyCount = countHeaderFrequency(chartMsg, options);
  const filterFrequencyCount = countFilterFrequency(chartMsg, options);
  //Varaibles of extracted data from command && overhearing
  let extractedHeaders = extract.headers(
    chartMsg,
    headerFrequencyCount,
    options
  );
  const extractedFilteredValues = extract.filterValues(
    chartMsg,
    filterFrequencyCount,
    options
  );

  //Holds all charts
  let charts = [];
  console.log(intent);

  switch (intent) {
    case "histogram":
      extractedHeaders = keepThis(chartMsg, extractedHeaders, "nominal");
      for (let i = 0; i < extractedHeaders.length; i++) {
        charts.push(
          createHistogram(
            chartMsg,
            extractedHeaders[i],
            extractedFilteredValues,
            headerFrequencyCount
          )
        );
      }
      break;
    case "bar":
      if (!options.useCovidDataset) {
        const findQuantitative = findAndRemoveOtherTypes(
          chartMsg,
          extractedHeaders,
          "quantitative"
        );
        extractedHeaders = findQuantitative.extractedHeaders;
        console.log(extractedHeaders);

        if (!findQuantitative.typeFound) {
          for (let i = 0; i < extractedHeaders.length; i++) {
            charts.push(
              createHistogram(
                chartMsg,
                extractedHeaders[i],
                extractedFilteredValues,
                headerFrequencyCount
              )
            );
          }
        } else {
          for (let i = 1; i < extractedHeaders.length; i++) {
            let twoExtractedHeaders = [
              extractedHeaders[0],
              extractedHeaders[i],
            ];
            charts.push(
              createBar(
                chartMsg,
                twoExtractedHeaders,
                extractedFilteredValues,
                headerFrequencyCount
              )
            );
          }
        }
      } else {
        extractedHeaders = keepThis(chartMsg, extractedHeaders, "nominal");

        for (let i = 0; i < extractedHeaders.length; i++) {
          charts.push(
            createHistogram(
              chartMsg,
              extractedHeaders[i],
              extractedFilteredValues,
              headerFrequencyCount
            )
          );
        }
      }
      break;
    case "line":
      const findTemporalAndQuantitativeObj = findTemporalAndQuantitative(
        chartMsg,
        extractedHeaders
      );
      extractedHeaders = findTemporalAndQuantitativeObj.extractedHeaders;
      console.log(findTemporalAndQuantitativeObj.quantitativeFound);

      if (
        !findTemporalAndQuantitativeObj.temporalFound ||
        !findTemporalAndQuantitativeObj.quantitativeFound
      ) {
        return charts;
      }
      if (extractedHeaders.length == 2) {
        charts.push(
          createLine(
            chartMsg,
            extractedHeaders,
            extractedFilteredValues,
            headerFrequencyCount
          )
        );
      } else if (extractedHeaders.length > 2) {
        let threeExtractedHeaders = [];
        for (let i = 2; i < extractedHeaders.length; i++) {
          threeExtractedHeaders = [
            extractedHeaders[0],
            extractedHeaders[1],
            extractedHeaders[i],
          ];
          charts.push(
            createLine(
              chartMsg,
              threeExtractedHeaders,
              extractedFilteredValues,
              headerFrequencyCount
            )
          );
        }
      }
      break;
    case "map":
      if (options.useCovidDataset) {
        extractedHeaders = keepThis(chartMsg, extractedHeaders, "nominal");
      }
      findAndRemoveOtherTypes(chartMsg, extractedHeaders, "map");

      if (extractedHeaders.length >= 2) {
        for (let i = 1; i < extractedHeaders.length; i++) {
          let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[i]];
          charts.push(
            createMap(
              chartMsg,
              twoExtractedHeaders,
              extractedFilteredValues,
              headerFrequencyCount
            )
          );
        }
      }
      break;
    case "heatmap":
      extractedHeaders = removeOtherTypes(
        chartMsg,
        extractedHeaders,
        "temporal"
      );
      if (options.useCovidDataset) {
        extractedHeaders = removeOtherTypes(
          chartMsg,
          extractedHeaders,
          "quantitative"
        );
      }
      for (let i = 1; i < extractedHeaders.length; i++) {
        charts.push(
          createHeatmap(
            chartMsg,
            [extractedHeaders[0], extractedHeaders[i]],
            extractedFilteredValues,
            headerFrequencyCount
          )
        );
      }
      break;
    default:
      break;
  }
  return charts;
};