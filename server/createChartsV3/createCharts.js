/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
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
const findQuantitativeAndSwitch = require("./charts/helpers/findQuantitativeAndSwitch");

module.exports = (intent, chartMsg, options, isPython) => {
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
  console.log(intent, "******************");

  // console.log(chartMsg.command, extractedHeaders, isPython);
  switch (intent) {
    case "histogram":
      if (options.useCovidDataset) {
        extractedHeaders = keepThis(chartMsg, extractedHeaders, "nominal");
      }
      for (let i = 0; i < extractedHeaders.length; i++) {
        charts.push(
          createHistogram(
            chartMsg,
            extractedHeaders[i],
            extractedFilteredValues,
            headerFrequencyCount,
            filterFrequencyCount,
            options
          )
        );
      }
      break;
    case "bar":
      const findQuantitative = findQuantitativeAndSwitch(
        chartMsg,
        extractedHeaders,
        "quantitative"
      );

      extractedHeaders = findQuantitative.extractedHeaders;
      extractedHeaders = removeOtherTypes(chartMsg, extractedHeaders, "map");

      if (!findQuantitative.typeFound) {
        for (let i = 0; i < extractedHeaders.length; i++) {
          charts.push(
            createHistogram(
              chartMsg,
              extractedHeaders[i],
              extractedFilteredValues,
              headerFrequencyCount,
              filterFrequencyCount,
              options
            )
          );
        }
      } else {
        for (let i = 1; i < extractedHeaders.length; i++) {
          let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[i]];
          charts.push(
            createBar(
              chartMsg,
              twoExtractedHeaders,
              extractedFilteredValues,
              headerFrequencyCount,
              filterFrequencyCount,
              options
            )
          );
        }
      }
      // } else {
      //   extractedHeaders = keepThis(chartMsg, extractedHeaders, "nominal");

      //   for (let i = 0; i < extractedHeaders.length; i++) {
      //     charts.push(
      //       createHistogram(
      //         chartMsg,
      //         extractedHeaders[i],
      //         extractedFilteredValues,
      //         headerFrequencyCount,
      //         filterFrequencyCount
      //       )
      //     );
      //   }
      // }
      break;
    case "line":
      if (extractedHeaders == 0) {
        break;
      }
      const findTemporalAndQuantitativeObj = findTemporalAndQuantitative(
        chartMsg,
        extractedHeaders
      );

      extractedHeaders = findTemporalAndQuantitativeObj.extractedHeaders;
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
            headerFrequencyCount,
            filterFrequencyCount,
            options
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
              headerFrequencyCount,
              filterFrequencyCount,
              options
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
              headerFrequencyCount,
              filterFrequencyCount,
              options
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
      extractedHeaders = removeOtherTypes(chartMsg, extractedHeaders, "map");
      if (extractedHeaders.length < 2) {
        break;
      }
      for (let i = 1; i < extractedHeaders.length; i++) {
        charts.push(
          createHeatmap(
            chartMsg,
            [extractedHeaders[0], extractedHeaders[i]],
            extractedFilteredValues,
            headerFrequencyCount,
            filterFrequencyCount,
            options
          )
        );
      }
      break;
    default:
      break;
  }
  return charts;
};
