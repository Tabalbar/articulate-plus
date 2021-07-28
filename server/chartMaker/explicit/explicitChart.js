const createVector = require("../createVector");
const nlp = require("compromise");
const mark = require("../helperFunctions/mark");
const encoding = require("./encoding");
const transform = require("../helperFunctions/transform");
const createDate = require("../helperFunctions/createDate");
const title = require("../helperFunctions/title");
const map = require("../specialGraphs/map");

// let chart = chartMaker.chartMaker(explicitChart, synonymCommand, attributes, data, headerMatrix, command, headerFreq, randomChart)

module.exports = (intent, chartMsg) => {
  let extractedHeaders = extractHeaders(chartMsg.command, chartMsg.attributes);
  if (extractedHeaders.length == 0) {
    return "";
  }
  const headerMatrix = createVector(chartMsg.attributes, chartMsg.data);
  let filteredHeaders = extractFilteredHeaders(chartMsg.command, headerMatrix);
  let chartObj = {
    charts: {
      spec: {
        title: "",
        mark: "",
        width: 400,
        height: 220,
        transform: [],
        concat: [],
        encoding: {
          column: {},
          y: {},
          x: {},
        },
        initialized: createDate(),
        timeChosen: "",
        timeClosed: "",
        timeSpentHovered: 0,
        data: { name: "table" }, // note: vega-lite data attribute is a plain object instead of an array
        command: chartMsg.command,
      },
    },
  };
  chartObj = mark(chartObj, intent);
  chartObj = encoding(
    chartObj,
    intent,
    extractedHeaders,
    chartMsg.data,
    chartMsg.command
  );
  if (chartObj == "") {
    return "";
  }
  chartObj = transform(chartMsg.data, filteredHeaders, chartObj, intent);
  chartObj.charts.spec.title = title(extractedHeaders, intent, filteredHeaders);
  return chartObj;
};

function extractHeaders(command, headers) {
  let doc = nlp(command);
  let extractedHeaders = [];
  for (let i = 0; i < headers.length; i++) {
    if (doc.has(headers[i].toLowerCase())) {
      extractedHeaders.push(headers[i]);
    }
  }
  let accessors = [];
  return extractedHeaders;
}

function extractFilteredHeaders(command, headerMatrix) {
  let doc = nlp(command);
  let extractedFilteredHeaders = [];
  doc.nouns().toSingular();

  for (let i = 0; i < headerMatrix.length; i++) {
    extractedFilteredHeaders[headerMatrix[i][0]] = [];
    for (let j = 1; j < headerMatrix[i].length; j++) {
      if (doc.has(headerMatrix[i][j])) {
        extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][j]);
      }
    }
  }
  return extractedFilteredHeaders;
}
