/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const levenshtein = require("fast-levenshtein");
const createDate = require("../helperFunctions/createDate");
const findType = require("../helperFunctions/findType");
const CovidColors = require("../../../createCharts/static/CovidColors");
const CovidSort = require("../../../createCharts/static/CovidSort");
const getExplicitChartType = require("../../../createCharts/explicit/ExplicitChart");

//****Pivotting mark types only works with covid dataset
module.exports = (charts, chartMsg, modifiedChartOptions) => {
  let { extractedHeaders, extractedFilters, extractedMarkType } =
    extractInfo(chartMsg);
  let chartsToReturn = [];

  for (let i = 0; i < charts.length; i++) {
    let chart = { spec: charts[i] };
    let chartObj = {
      charts: { spec: {} },
    };

    // if (modifiedChartOptions.useCovidDataset) {
    //   if (extractedMarkType.length > 0) {
    //     chart = createChartWithMarkType(chart, extractedMarkType, chartMsg);
    //   }
    // }
    // extractedHeaders.push(chart.spec.defaultHeader);
    // console.log(extractedHeaders);
    if (!chart.spec.defaultHeader) {
      for (let j = 0; j < extractedHeaders.length; j++) {
        chart = createChartWithHeader(chart, extractedHeaders[j], chartMsg);
      }
      for (let j = 0; j < extractedFilters.length; j++) {
        if (extractedFilters[j].filters.length > 0) {
          chart = createChartWithFilter(chart, extractedFilters[j], chartMsg);
        }
      }
    }
    chart = cleanChart(
      chart,
      chartMsg,
      extractedHeaders,
      extractedFilters,
      extractedMarkType
    );
    chartObj.charts.spec = chart.spec;

    chartsToReturn.push(chartObj);
  }

  return chartsToReturn;
};

function extractInfo(chartMsg) {
  let words = chartMsg.command.split(" ");

  //Initialize values
  let extractedMarkType = "";
  let extractedHeaders = [];
  let extractedFilters = [];

  //Checking for spoken mark types
  if (getExplicitChartType(chartMsg.command)) {
    extractedMarkType = getExplicitChartType(chartMsg.command);
  }
  //Checking for spoken attributes
  for (let i = 0; i < chartMsg.attributes.length; i++) {
    if (
      chartMsg.command
        .toLowerCase()
        .includes(chartMsg.attributes[i].toLowerCase()) &&
      findType(chartMsg.attributes[i], chartMsg.data) == "nominal"
    ) {
      extractedHeaders.push(chartMsg.attributes[i]);
    }
  }

  //checking for spoken filters
  for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    extractedFilters.push({
      header: chartMsg.featureMatrix[i][0],
      filters: [],
    });
    for (let j = 1; j < chartMsg.featureMatrix[i].length; j++) {
      if (
        chartMsg.command
          .toLowerCase()
          .includes(chartMsg.featureMatrix[i][j].toLowerCase())
      ) {
        extractedFilters[i].filters.push(chartMsg.featureMatrix[i][j]);
      } else {
        for (let n = 0; n < words.length; n++) {
          if (
            levenshtein.get(
              words[n].toLowerCase(),
              chartMsg.featureMatrix[i][j].toLowerCase()
            ) == 1
          ) {
            extractedFilters[i].filters.push(chartMsg.featureMatrix[i][j]);
          }
        }
      }
    }
  }
  return { extractedHeaders, extractedFilters, extractedMarkType };
}

function createChartWithFilter(chart, extractedFilter, chartMsg) {
  if (chart.spec.hasOwnProperty("layer")) {
    let oneOfFilters = [];
    for (let i = 0; i < extractedFilter.filters.length; i++) {
      oneOfFilters.push(extractedFilter.filters[i]);
    }
    chart.spec.layer[1].transform.push({
      filter: {
        field: extractedFilter.header,
        oneOf: oneOfFilters,
      },
    });
  }

  return chart;
}

function createChartWithMarkType(chart, extractedMarkType, chartMsg) {
  if (chart.spec.hasOwnProperty("layer") && extractedMarkType !== "map") {
    chart.spec.defaultHeader = chart.spec.layer[1].encoding.color.field;
    delete chart.spec.projection;
    delete chart.spec.layer;
  } else {
    chart.spec.defaultHeader = chart.spec.encoding.color.field;
  }
  if (extractedMarkType == "bar") {
    chart.spec.mark = "bar";
    chart.spec.defaultHeader = chart.spec.encoding.color.field;
  } else if (extractedMarkType == "line") {
    chart.spec.mark = "line";
    chart.spec.defaultHeader = chart.spec.encoding.color.field;
  } else if (extractedMarkType == "map") {
    let obj = {
      data: chart.spec.data,
      mark: { type: "geoshape", stroke: "black" },
      transform: [
        {
          lookup: "map",
          from: {
            data: {
              url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
              format: { type: "topojson", feature: "counties" },
            },
            key: "id",
          },
          as: "geo",
        },
      ],
      encoding: {
        color: {
          field: chart.spec.encoding.color.field,
          type: "nominal",
          scale: { range: CovidColors(chart.spec.encoding.color.field) },
          sort: CovidSort(chart.spec.encoding.color.field, chartMsg.data),
        },
        shape: { field: "geo", type: "geojson" },
      },
    };
    delete chart.spec.data;
    delete chart.spec.mark;
    delete chart.spec.transform;
    delete chart.spec.encoding;
    delete chart.spec.concat;
    chart.spec.projection = { type: "albersUsa" };
    chart.spec.layer = [
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
  return chart;
}

function createChartWithHeader(chart, extractedHeader, chartMsg) {
  if (chart.spec.hasOwnProperty("layer")) {
    chart.spec.layer[1].encoding.color.field = extractedHeader;
    chart.spec.layer[1].encoding.color.scale.range =
      CovidColors(extractedHeader);
    chart.spec.layer[1].encoding.color.sort = CovidSort(
      extractedHeader,
      chartMsg.data
    );
  }

  return chart;
}

function createNewTitle(
  chart,
  extractedHeaders,
  extractedFilters,
  extractedMarkType
) {
  let chartTitle = "";
  let headerLength = extractedHeaders.length;
  let filteredHeaderLength = 0;
  for (let i = 0; i < extractedFilters.length; i++) {
    for (let j = 0; j < extractedFilters[i].filters.length; j++) {
      filteredHeaderLength++;
    }
  }

  let filteredTitles = [];
  let headerTitles = [];

  if (headerLength > 3) {
    headerLength = 3;
  }
  //Capitalize Header titles
  for (let i = 0; i < extractedHeaders.length; i++) {
    let headers = extractedHeaders[i].split(" ");
    let title = "";
    for (let n = 0; n < headers.length; n++) {
      title += headers[n].charAt(0).toUpperCase() + headers[n].slice(1) + " ";
    }
    if (!(chart.spec.hasOwnProperty("layer") && extractedHeaders[i] == "map")) {
      headerTitles.push(title);
    }
  }

  //Capitalize Filter titles
  for (let i = 0; i < extractedFilters.length; i++) {
    for (let j = 0; j < extractedFilters[i].filters.length; j++) {
      let filters = extractedFilters[i].filters[j].split(" ");
      let title = "";
      for (let n = 0; n < filters.length; n++) {
        title += filters[n].charAt(0).toUpperCase() + filters[n].slice(1) + " ";
      }
      filteredTitles.push(title);
    }
  }

  if (extractedMarkType == "map") {
    chartTitle = "Map of " + headerTitles[0];
  } else {
    switch (headerLength) {
      case 1:
        switch (extractedMarkType) {
          case "bar":
            chartTitle += "Histogram of " + headerTitles[0];
            break;
          case "histogram":
            chartTitle += "Histogram of " + headerTitles[0];
            break;
          case "line":
            chartTitle += "Line chart of " + headerTitles[0];
            break;
          case "heatmap":
            chartTitle += "Line chart of " + headerTitles[0];
            break;
          case "scatter":
            chartTitle += "Scatter plot of " + extractedHeaders[0];
            break;
        }
        break;
      case 2:
        switch (extractedMarkType) {
          case "bar":
            chartTitle += "Bar chart of " + headerTitles[0] + headerTitles[1];
            break;
          case "line":
            chartTitle +=
              "Line chart of " + headerTitles[0] + " vs " + headerTitles[1];
            break;
          case "heatmap":
            chartTitle += "Heatmap sum of " + headerTitles[0] + headerTitles[1];
            break;
          case "scatter":
            chartTitle +=
              "Scatter plot of " + headerTitles[0] + " vs " + headerTitles[1];
            break;
        }
        break;

      case 3:
        switch (extractedMarkType) {
          case "bar":
            chartTitle +=
              "Bar chart of " +
              headerTitles[0] +
              headerTitles[1] +
              " Colored by " +
              headerTitles[2];
            break;
          case "line":
            chartTitle +=
              "Line chart of " +
              headerTitles[0] +
              headerTitles[1] +
              " Colored by " +
              headerTitles[2];
            break;
          case "scatter":
            chartTitle +=
              "Scatter plot of " +
              headerTitles[0] +
              headerTitles[1] +
              " Sized by " +
              headerTitles[2];

            break;
        }
        break;
      default:
        return "";
    }
  }
  if (filteredHeaderLength > 0) {
    chartTitle += " Filtered by ";
    for (let i = 0; i < filteredTitles.length; i++) {
      if (i == filteredTitles.length - 1) {
        chartTitle += filteredTitles[i];
        break;
      }
      chartTitle += filteredTitles[i] + " and ";
    }
  }
  return chartTitle;
}

function cleanChart(
  chart,
  chartMsg,
  extractedHeaders,
  extractedFilters,
  extractedMarkType
) {
  let time = (new Date() - new Date(chartMsg.deltaTime)) / 1000 / 60;
  time = Math.round(time * 100) / 100;
  chart.spec.deltaTime = time;
  chart.spec.visible = false;
  chart.spec.timeChosen = [];
  chart.spec.timeClosed = [];
  chart.spec.initialized = createDate();
  chart.spec.pivotFromId = chart.spec.id;
  chart.spec.pivotThis = false;
  chart.spec.title = createNewTitle(
    chart,
    extractedHeaders,
    extractedFilters,
    extractedMarkType
  );
  return chart;
}

//TODO create = function that checks if charts were actually made.
//return 0 has length to server request and the server request
//can check if length is 0. Then make arty say, i dont have any charts for you.
