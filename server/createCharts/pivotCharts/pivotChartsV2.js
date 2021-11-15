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
    let { defaultMarkType, defaultHeader, defaultFilters, id } =
      extractInfoFromChart(charts[i], chartMsg);
    let { extractedHeaders, extractedFilters, extractedMarkType } =
      extractInfo(chartMsg);

    //Replace Mark type
    if (extractedMarkType == "") {
      markTypeToUse = defaultMarkType;
    } else {
      markTypeToUse = extractedMarkType;
    }

    //Replace attributes //Had to comment because filters have same name as attributes
    //IE: very low diabetes rate has the word diabetes in it.
    // if (extractedHeaders.length == 0) {
    for (let j = 0; j < defaultHeader.length; j++) {
      headersToUse.push(defaultHeader[j]);
    }
    // } else {
    for (let j = 0; j < extractedHeaders.length; j++) {
      headersToUse.push(extractedHeaders[j]);
    }
    // }
    //add Filters
    for (let j = 0; j < defaultFilters.length; j++) {
      filtersToUse.push(defaultFilters[j]);
    }

    for (let j = 0; j < extractedFilters.length; j++) {
      filtersToUse.push(extractedFilters[j]);
    }

    //Create command to use for createing charts but save old command to replace
    const oldCommand = chartMsg.command;
    chartMsg.command = buildCommand(markTypeToUse, headersToUse, filtersToUse);
    let pivotedCharts = createCharts(markTypeToUse, chartMsg, options);

    chartMsg.command = oldCommand;

    for (let j = 0; j < pivotedCharts.length; j++) {
      pivotedCharts[j] = cleanChart(pivotedCharts[j], chartMsg, id);
    }
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
    for (let j = 1; j < chartMsg.featureMatrix[i].length; j++) {
      if (
        chartMsg.command
          .toLowerCase()
          .includes(chartMsg.featureMatrix[i][j].toLowerCase())
      ) {
        extractedFilters.push(chartMsg.featureMatrix[i][j]);
      } else {
        for (let n = 0; n < words.length; n++) {
          if (
            levenshtein.get(
              words[n].toLowerCase(),
              chartMsg.featureMatrix[i][j].toLowerCase()
            ) == 1
          ) {
            extractedFilters.push(chartMsg.featureMatrix[i][j]);
          }
        }
      }
    }
  }
  return { extractedHeaders, extractedFilters, extractedMarkType };
}

function extractInfoFromChart(chart, chartMsg) {
  let defaultHeader = [];
  let defaultFilters = [];
  let defaultMarkType = "";
  let id = 0;
  // for (let j = 0; j < chartMsg.featureMatrix.length; j++) {
  //   defaultFilters[chartMsg.featureMatrix[j][0]] = [];
  // }
  if (chart.hasOwnProperty("layer")) {
    defaultMarkType = "map";
    defaultHeader.push(chart.layer[1].encoding.color.field);
    for (let i = 1; i < chart.layer[1].transform.length; i++) {
      for (
        let j = 0;
        j < chart.layer[1].transform[i].filter.oneOf.length;
        j++
      ) {
        defaultFilters.push(chart.layer[1].transform[i].filter.oneOf[j]);
      }
    }
  } else if (chart.mark.hasOwnProperty("type")) {
    defaultMarkType = chart.mark.type;
    if (findType(chart.encoding.x.field, chartMsg.data) == "nominal") {
      defaultHeader.push(chart.encoding.x.field);
    }
    if (findType(chart.encoding.y.field, chartMsg.data) == "nominal") {
      defaultHeader.push(chart.encoding.y.field);
    }
    if (chart.encoding.hasOwnProperty("color")) {
      if (findType(chart.encoding.color.field, chartMsg.data) == "nominal") {
        defaultHeader.push(chart.encoding.color.field);
      }
    }

    for (let i = 0; i < chart.transform.length; i++) {
      for (let j = 0; j < chart.transform[i].filter.oneOf.length; j++) {
        defaultFilters.push(chart.transform[i].filter.oneOf[j]);
      }
    }
  } else {
    defaultMarkType = chart.mark;
    if (defaultMarkType == "rect") {
      defaultMarkType = "heatmap";
    }
    if (findType(chart.encoding.x.field, chartMsg.data) == "nominal") {
      defaultHeader.push(chart.encoding.x.field);
    }
    if (chart.encoding.y.hasOwnProperty("field")) {
      if (findType(chart.encoding.y.field, chartMsg.data) == "nominal") {
        defaultHeader.push(chart.encoding.y.field);
      }
    }
    if (chart.encoding.hasOwnProperty("color")) {
      if (chart.encoding.color.hasOwnProperty("field")) {
        if (findType(chart.encoding.color.field, chartMsg.data) == "nominal") {
          defaultHeader.push(chart.encoding.color.field);
        }
      }
    }

    for (let i = 0; i < chart.transform.length; i++) {
      for (let j = 0; j < chart.transform[i].filter.oneOf.length; j++) {
        defaultFilters.push(chart.transform[i].filter.oneOf[j]);
      }
    }
  }
  id = chart.id;
  return {
    defaultMarkType: defaultMarkType,
    defaultHeader: defaultHeader,
    defaultFilters: defaultFilters,
    id: id,
  };
}

function cleanChart(chart, chartMsg, id) {
  let time = (new Date() - new Date(chartMsg.deltaTime)) / 1000 / 60;
  time = Math.round(time * 100) / 100;
  chart.deltaTime = time;
  chart.visible = false;
  chart.timeChosen = [];
  chart.timeClosed = [];
  chart.initialized = createDate();
  chart.pivotFromId = id;
  chart.pivotThis = false;
  return chart;
}

//TODO create = function that checks if charts were actually made.
//return 0 has length to server request and the server request
//can check if length is 0. Then make arty say, i dont have any charts for you.
