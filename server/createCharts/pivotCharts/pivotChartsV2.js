const levenshtein = require("fast-levenshtein");
const createDate = require("../helperFunctions/createDate");
const findType = require("../helperFunctions/findType");
const CovidColors = require("../static/CovidColors");
const CovidSort = require("../static/CovidSort");
const getExplicitChartType = require("../explicit/ExplicitChart");
const createCharts = require("../../createChartsV3/createCharts");

//****Pivotting mark types only works with covid dataset
module.exports = (charts, chartMsg, options) => {
  let chartsToReturn = [];
  for (let i = 0; i < charts.length; i++) {
    let markTypeToUse = "";
    let headersToUse = [];
    let filtersToUse = [];
    let newCommand = "";
    let { defaultMarkType, defaultHeader, defaultFilters } =
      extractInfoFromChart(charts[i], chartMsg);
    let { extractedHeaders, extractedFilters, extractedMarkType } =
      extractInfo(chartMsg);
    console.log(defaultFilters);
    if (extractedMarkType == "") {
      markTypeToUse = defaultMarkType;
    } else {
      markTypeToUse = extractedMarkType;
    }
    if (extractedHeaders.length == 0) {
      headersToUse.push(defaultHeader);
    } else {
      for (let i = 0; i < extractedHeaders.length; i++) {
        headersToUse.push(extractedHeaders[i]);
      }
    }
    for (let j = 0; j < defaultFilters.length; j++) {
      filtersToUse.push(defaultFilters[j]);
    }
    for (let j = 0; j < extractedFilters.length; j++) {
      filtersToUse.push(extractedFilters[j]);
    }
    newCommand = buildCommand(markTypeToUse, headersToUse, filtersToUse);
    chartMsg.command = newCommand;
    console.log(headersToUse, "eo");
    let pivotedCharts = createCharts(markTypeToUse, chartMsg, options);
    chartsToReturn.push(pivotedCharts);
  }
  chartsToReturn = chartsToReturn.flat();
  return chartsToReturn;
};

function buildCommand(mark, headers, filters) {
  let command = "";
  command += mark + " ";
  for (let i = 0; i < headers.length; i++) {
    command += headers[i] + " ";
  }
  for (let i = 0; i < filters.length; i++) {
    command += filters[i] + " ";
  }
  return command;
}

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
    // extractedFilters.push({
    //   header: chartMsg.featureMatrix[i][0],
    //   filters: [],
    // });
    for (let j = 1; j < chartMsg.featureMatrix[i].length; j++) {
      if (
        chartMsg.command
          .toLowerCase()
          .includes(chartMsg.featureMatrix[i][j].toLowerCase())
      ) {
        // extractedFilters[i].filters.push(chartMsg.featureMatrix[i][j]);
        extractedFilters.push(chartMsg.featureMatrix[i][j]);
      } else {
        for (let n = 0; n < words.length; n++) {
          if (
            levenshtein.get(
              words[n].toLowerCase(),
              chartMsg.featureMatrix[i][j].toLowerCase()
            ) == 1
          ) {
            // extractedFilters[i].filters.push(chartMsg.featureMatrix[i][j]);
            extractedFilters.push(chartMsg.featureMatrix[i][j]);
          }
        }
      }
    }
  }
  return { extractedHeaders, extractedFilters, extractedMarkType };
}

function extractInfoFromChart(chart, chartMsg) {
  let defaultHeader = "";
  let defaultFilters = [];
  let defaultMarkType = "";
  // for (let j = 0; j < chartMsg.featureMatrix.length; j++) {
  //   defaultFilters[chartMsg.featureMatrix[j][0]] = [];
  // }
  if (chart.hasOwnProperty("layer")) {
    defaultMarkType = "map";
    defaultHeader = chart.layer[1].encoding.color.field;
    console.log(chart.layer[1].transform);

    for (let i = 1; i < chart.layer[1].transform.length; i++) {
      for (
        let j = 0;
        j < chart.layer[1].transform[i].filter.oneOf.length;
        j++
      ) {
        defaultFilters.push(chart.layer[1].transform[i].filter.oneOf[j]);
      }
    }
    // for (let i = 1; i < chart.layer[1].transform.length; i++) {
    //   for (let j = 0; j < chartMsg.featureMatrix.length; j++) {
    //     if (
    //       chart.layer[1].transform[i].filter.field ==
    //       chartMsg.featureMatrix[j][0]
    //     ) {
    //       for (
    //         let n = 0;
    //         n < chart.layer[1].transform[i].filter.oneOf.length;
    //         n++
    //       ) {
    //         defaultFilters[chartMsg.featureMatrix[j][0]].push(
    //           chart.layer[1].transform[i].filter.oneOf[n]
    //         );
    //       }
    //     }
    //   }
    // }
  } else {
    defaultMarkType = chart.mark;
    if (findType(chart.encoding.x.field, chartMsg.data) == "nominal") {
      defaultHeader = chart.encoding.x.field;
    } else if (findType(chart.encoding.y.field, chartMsg.data) == "nominal") {
      defaultHeader = chart.encoding.x.field;
    } else if (
      findType(chart.encoding.color.field, chartMsg.data) == "nominal"
    ) {
      defaultHeader = chart.encoding.x.field;
    }
    for (let i = 0; i < chart.transform.length; i++) {
      for (let j = 0; j < chart.transform[i].filter.oneOf.length; j++) {
        defaultFilters.push(chart.transform[i].filter.oneOf[j]);
      }
    }
    // for (let i = 0; i < chart.transform.length; i++) {
    //   for (let j = 0; j < chartMsg.featureMatrix.length; j++) {
    //     if (chart.transform[i].filter.field == chartMsg.featureMatrix[j][0]) {
    //       for (let n = 0; n < chart.transform[i].filter.oneOf.length; n++) {
    //         defaultFilters[chartMsg.featureMatrix[j][0]].push(
    //           chart.transform[i].filter.oneOf[n]
    //         );
    //       }
    //     }
    //   }
    // }
  }
  return {
    defaultMarkType: defaultMarkType,
    defaultHeader: defaultHeader,
    defaultFilters: defaultFilters,
  };
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
    console.log(title);
    if (!(chart.spec.hasOwnProperty("layer") && extractedHeaders[i] == "map")) {
      console.log(i, "jjd");

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
  console.log(filteredHeaderLength);
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
