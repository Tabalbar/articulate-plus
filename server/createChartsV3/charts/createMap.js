/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const covidColors = require("./covidHelpers/covidColors");
const covidSort = require("./covidHelpers/covidSort");
const createTitle = require("./helpers/specifications/createTitle");
const createTransform = require("./helpers/specifications/createTransform");
const createChartTemplate = require("./createChartTemplate");

module.exports = (
  chartMsg,
  extractedHeaders,
  extractedFilteredValues,
  headerFrequencyCount,
  filterFrequencyCount,
  options,
  isPython,
  pythonData
) => {
  let chart = createChartTemplate(
    chartMsg,
    headerFrequencyCount,
    filterFrequencyCount
  );
  chart.height = 300;
  if (isPython) {
    chart.data = {
      values: pythonData,
    };
    chart.transform.push({
      lookup: extractedHeaders[0],
      from: {
        data: {
          url: "https://vega.github.io/vega-lite/data/us-10m.json",
          format: { type: "topojson", feature: "counties" },
        },
        key: "id",
      },
      as: "geo",
    });
    chart.projection = { type: "albersUsa" };
    chart.mark = "geoshape";
    chart.encoding = {
      color: {
        field: extractedHeaders[1],
        type: "nominal",
        legend: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
        scale: {
          range: options.useCovidDataset
            ? covidColors(extractedHeaders[1])
            : [],
        },
        sort: options.useCovidDataset
          ? covidSort(extractedHeaders[1], chartMsg.data)
          : [],
      },
      shape: { field: "geo", type: "geojson" },
    };
    // chart.data = {
    //   url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
    //   format: { type: "topojson", feature: "counties" },
    // };
    // chart.transform.push({
    //   lookup: "id",
    //   from: {
    //     data: {
    //       values: pythonData,
    //     },
    //     key: extractedHeaders[0],
    //     fields: [extractedHeaders[1]],
    //   },
    // });
    // chart.projection = { type: "albersUsa" };
    // chart.mark = "geoshape";
    // chart.encoding = {
    //   color: {
    //     field: extractedHeaders[1],
    //     type: "nominal",
    //     legend: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
    //     scale: {
    //       range: options.useCovidDataset
    //         ? covidColors(extractedHeaders[1])
    //         : [],
    //     },
    //     sort: options.useCovidDataset
    //       ? covidSort(extractedHeaders[1], chartMsg.data)
    //       : [],
    //   },
    // };
  } else {
    chart.transform.push({
      lookup: "fips",
      from: {
        data: {
          url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
          format: { type: "topojson", feature: "counties" },
        },
        key: "id",
      },
      as: "geo",
    });

    let obj = {};
    chart = createTransform(chart, chartMsg, extractedFilteredValues);

    obj = {
      data: chart.data,
      mark: { type: "geoshape", stroke: "black" },
      transform: chart.transform,
      encoding: {
        color: {
          field: extractedHeaders[1],
          type: "nominal",
          legend: { labelFontSize: 15, titleFontSize: 15, labelLimit: 2000 },
          scale: {
            range: options.useCovidDataset
              ? covidColors(extractedHeaders[1])
              : [],
          },
          sort: options.useCovidDataset
            ? covidSort(extractedHeaders[1], chartMsg.data)
            : [],
        },
        shape: { field: "geo", type: "geojson" },
      },
    };

    delete chart.mark;
    delete chart.transform;
    delete chart.encoding;
    delete chart.concat;
    chart.projection = { type: "albersUsa" };

    chart.layer = [
      {
        data: {
          url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
          format: {
            type: "topojson",
            feature: "states",
          },
        },
        mark: {
          type: "geoshape",
          fill: "lightgray",
          stroke: "white",
        },
      },
      obj,
    ];
  }

  chart = createTitle(chart, extractedHeaders, "map", extractedFilteredValues);
  return chart;
};
