const nlp = require("compromise");
const findFiltersInData = require("./findFiltersInData");
const countHeaderFrequency = require("./countHeaderFrequency");
const findType = require("./helperFunctions/findType");
const createDate = require("./helperFunctions/createDate");

const transform = require("./specifications/transform");
const mark = require("./specifications/mark");
const encoding = require("./specifications/encoding");
const title = require("./specifications/title");

module.exports = (intent, chartMsg, options) => {
  let extractedHeaders = extractHeaders(
    chartMsg.command,
    chartMsg.attributes,
    chartMsg.data,
    intent
  );
  let filteredHeaders = extractFilteredHeaders(
    chartMsg.command,
    chartMsg.data,
    chartMsg.attributes,
    chartMsg.command
  );
  const { headerFrequencyCount } = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    options
  );
  const headerKeys = Object.keys(headerFrequencyCount);
  for (let i = 0; i < headerKeys.length; i++) {
    for (let j = 0; j < headerFrequencyCount[headerKeys[i]].length; j++) {
      if (headerFrequencyCount[headerKeys[i]][j].count >= 5) {
        let found = false;
        for (let n = 0; n < extractedHeaders.length; n++) {
          if (
            extractedHeaders[n] == headerFrequencyCount[headerKeys[i]][j].header
          ) {
            found = true;
          }
        }
        if (!found) {
          extractedHeaders.push(headerFrequencyCount[headerKeys[i]][j].header);
        }
      }
    }
  }
  let charts = [];
  console.log(extractedHeaders);
  if (extractedHeaders.length == 1) {
    let chartObj = runAlgortihm(
      intent,
      extractedHeaders,
      chartMsg.data,
      headerFrequencyCount,
      chartMsg.command,
      options,
      filteredHeaders
    );
    charts.push(chartObj);
  } else {
    if (intent == "line") {
      if (extractedHeaders.length < 3) {
        let twoExtractedHeaders = [extractedHeaders[0], extractedHeaders[1]];
        let chartObj = runAlgortihm(
          intent,
          twoExtractedHeaders,
          chartMsg.data,
          headerFrequencyCount,
          chartMsg.command,
          options,
          filteredHeaders
        );
        charts.push(chartObj);
      }
      for (let j = 2; j < extractedHeaders.length; j++) {
        let threeExtractedHeaders = [];
        threeExtractedHeaders.push(
          extractedHeaders[0],
          extractedHeaders[1],
          extractedHeaders[j]
        );
        let chartObj = runAlgortihm(
          intent,
          threeExtractedHeaders,
          chartMsg.data,
          headerFrequencyCount,
          chartMsg.command,
          options,
          filteredHeaders
        );
        charts.push(chartObj);
      }
    } else {
      for (let j = 1; j < extractedHeaders.length; j++) {
        let twoExtractedHeaders = [];

        twoExtractedHeaders.push(extractedHeaders[0], extractedHeaders[j]);
        let chartObj = runAlgortihm(
          intent,
          twoExtractedHeaders,
          chartMsg.data,
          headerFrequencyCount,
          chartMsg.command,
          options,
          filteredHeaders
        );
        charts.push(chartObj);
      }
    }
  }

  return charts;
};

function runAlgortihm(
  intent,
  extractedHeaders,
  data,
  headerFrequencyCount,
  command,
  options,
  filteredHeaders
) {
  let chartObj = {
    charts: {
      spec: {
        title: "",
        width: 400,
        height: 220,
        mark: "",
        transform: [],
        concat: [],
        encoding: {
          column: {},
          y: {},
          x: {},
        },
        initialized: createDate(),
        timeChosen: [],
        timeClosed: [],
        timeSpentHovered: 0,
        data: { name: "table" }, // note: vega-lite data attribute is a plain object instead of an array
        command: command,
      },
    },
  };
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (extractedHeaders[i] == "map" && intent !== "map") {
      extractedHeaders.splice(i, 1);
      break;
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (
      (extractedHeaders[i] == "cases" || extractedHeaders[i] == "date") &&
      intent !== "line"
    ) {
      extractedHeaders.splice(i, 1);
      break;
    }
  }
  chartObj = mark(chartObj, intent);
  chartObj = encoding(
    chartObj,
    intent,
    extractedHeaders,
    data,
    headerFrequencyCount,
    command,
    options
  );
  if (chartObj == "") {
    charts.push("");
  }
  chartObj = transform(data, filteredHeaders, chartObj, intent);
  chartObj.charts.spec.title = title(extractedHeaders, intent, filteredHeaders);
  return chartObj;
}

function extractHeaders(command, headers, data, intent) {
  let doc = nlp(command);
  let extractedHeaders = [];
  for (let i = 0; i < headers.length; i++) {
    if (
      doc.has(headers[i].toLowerCase()) ||
      doc.has(headers[i].toLowerCase().toLowerCase())
    ) {
      extractedHeaders.push(headers[i]);
    }
  }
  let wordPosition = [];
  for (let i = 0; i < extractedHeaders.length; i++) {
    wordPosition.push({
      index: command.indexOf(extractedHeaders[i].toLowerCase()),
      header: extractedHeaders[i],
    });
  }
  wordPosition.sort((a, b) => a.index - b.index);
  extractedHeaders = [];
  for (let i = 0; i < wordPosition.length; i++) {
    extractedHeaders.push(wordPosition[i].header);
  }

  if (intent === "map") {
    let mapFound = false;
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "map") {
        mapFound = true;
      }
    }
    if (!mapFound) {
      for (let i = 0; i < headers.length; i++) {
        if (headers[i] == "map") {
          extractedHeaders.push(headers[i]);
        }
      }
    }
  }

  if (intent === "line") {
    let dateFound = false;
    let casesFound = false;

    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "cases") {
        casesFound = true;
      }
      if (extractedHeaders[i] == "date") {
        dateFound = true;
      }
    }

    if (!dateFound) {
      extractedHeaders.push("date");
    }
    if (!casesFound) {
      extractedHeaders.push("cases");
    }
  }

  if (doc.has("overtime") || doc.has("time")) {
    let foundTime = false;
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (findType(extractedHeaders[i], data) === "temporal") {
        foundTime = true;
        break;
      }
    }
    if (!foundTime) {
      for (let i = 0; i < headers.length; i++) {
        if (findType(headers[i], data) === "temporal") {
          extractedHeaders.push(headers[i]);
          break;
        }
      }
    }
  }
  return extractedHeaders;
}

function extractFilteredHeaders(command, data, headers, command) {
  const headerMatrix = findFiltersInData(headers, data);
  let doc = nlp(command);
  let extractedFilteredHeaders = [];
  let foundTimeHeader = false;
  for (let i = 0; i < headerMatrix.length; i++) {
    extractedFilteredHeaders[headerMatrix[i][0]] = [];
    for (let n = 1; n < headerMatrix[i].length; n++) {
      if (doc.has(headerMatrix[i][n])) {
        extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][n]);
      }
    }

    if (findType(headerMatrix[i][0], data) === "temporal" && !foundTimeHeader) {
      const { foundTime, timeHeader } = extractHeadersWithoutFilter(
        doc,
        headers,
        data,
        command
      );
      if (!foundTime) {
        findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]]);
        command += " " + headerMatrix[i][0];
        foundTimeHeader = true;
      } else {
        if (timeHeader === headerMatrix[i][0]) {
          findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]]);
        }
      }
    }
  }

  function findDates(docCommand, header) {
    if (
      docCommand.match("to") ||
      docCommand.match("through") ||
      docCommand.match("and")
    ) {
      let termsBefore = docCommand.before("to").terms().out("array");
      let termsAfter = docCommand.after("to").terms().out("array");
      const yearBefore = termsBefore[termsBefore.length - 1];
      const yearAfter = termsAfter[0];
      if (!isNaN(yearBefore) && !isNaN(yearAfter)) {
        header.push(yearBefore);
        header.push(yearAfter);
      }
    }
  }

  function extractHeadersWithoutFilter(docCommand, headers, data) {
    let extractedHeaders = [];
    let foundTime = false;
    let index;
    for (let i = 0; i < headers.length; i++) {
      if (
        docCommand.has(headers[i]) &&
        findType(headers[i], data) === "temporal"
      ) {
        index = i;
        foundTime = true;
        break;
      }
    }
    let timeHeader = headers[index];
    return { foundTime, timeHeader };
  }
  return extractedFilteredHeaders;
}
