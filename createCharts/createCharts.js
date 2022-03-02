const nlp = require("compromise");
const findFiltersInData = require("./findFiltersInData");
const countHeaderFrequency = require("./countHeaderFrequency");
const findType = require("./helperFunctions/findType");
const createDate = require("./helperFunctions/createDate");

const levenshtein = require("fast-levenshtein");

const transform = require("./specifications/transform");
const mark = require("./specifications/mark");
const encoding = require("./specifications/encoding");
const title = require("./specifications/title");
const countFilterFrequency = require("./countFilterFrequency");

module.exports = (intent, chartMsg, options) => {
  const headerFrequencyCount = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    options
  );

  let extractedHeaders = [];
  extractedHeaders = extractHeaders(
    chartMsg.command,
    chartMsg.attributes,
    chartMsg.data,
    intent,
    options,
    chartMsg
  );
  if (options.window.toggle) {
    const headerKeys = Object.keys(headerFrequencyCount);
    let headersToSort = [];
    for (let i = 0; i < headerKeys.length; i++) {
      for (let j = 0; j < headerFrequencyCount[headerKeys[i]].length; j++) {
        headersToSort.push(headerFrequencyCount[headerKeys[i]][j]);
      }
    }
    let sortedHeaders = headersToSort.sort((a, b) =>
      a.count < b.count ? 1 : -1
    );
    //**POSSIBLE BUG INDEX OUT OF RANGE**.
    for (let i = 0; i < 4; i++) {
      if (sortedHeaders[i].count >= options.threshold) {
        let found = false;
        for (let j = 0; j < extractedHeaders.length; j++) {
          if (sortedHeaders[i] == extractedHeaders[j]) {
            found = true;
          }
        }
        if (!found) {
          extractedHeaders.push(sortedHeaders[i].header);
        }
      }
    }
  }

  extractedHeaders = checkDuplicates(extractedHeaders);
  let casesFound = false;
  let dateFound = false;
  if (intent !== "line") {
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "cases") {
        casesFound = true;
      }
      if (extractedHeaders[i] == "date") {
        dateFound = true;
      }

      if (casesFound && dateFound) {
        intent = "line";
      }
    }

    if (casesFound && !dateFound) {
      extractedHeaders.unshift("date");
    }
    if (!casesFound && dateFound) {
      extractedHeaders.unshift("cases");
    }
  }
  const filterFrequencyCount = countFilterFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.data,
    options
  );
  let filteredHeaders = extractFilteredHeaders(
    chartMsg.command,
    chartMsg.data,
    chartMsg.attributes,
    chartMsg.command,
    filterFrequencyCount,
    options
  );

  let charts = [];
  if (extractedHeaders.length == 1) {
    let chartObj = runAlgortihm(
      intent,
      extractedHeaders,
      chartMsg.data,
      headerFrequencyCount,
      chartMsg.command,
      options,
      filteredHeaders,
      chartMsg.attributes,
      chartMsg.deltaTime,
      filterFrequencyCount
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
          filteredHeaders,
          chartMsg.attributes,
          chartMsg.deltaTime,
          filterFrequencyCount
        );
        charts.push(chartObj);
      } else {
        for (let j = 2; j < extractedHeaders.length; j++) {
          let threeExtractedHeaders = [
            extractedHeaders[0],
            extractedHeaders[1],
            extractedHeaders[j],
          ];

          let chartObj = runAlgortihm(
            intent,
            threeExtractedHeaders,
            chartMsg.data,
            headerFrequencyCount,
            chartMsg.command,
            options,
            filteredHeaders,
            chartMsg.attributes,
            chartMsg.deltaTime,
            filterFrequencyCount
          );
          charts.push(chartObj);
        }
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
          filteredHeaders,
          chartMsg.attributes,
          chartMsg.deltaTime,
          filterFrequencyCount
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
  filteredHeaders,
  headers,
  deltaTime,
  filterFrequencyCount
) {
  let time = (new Date() - new Date(deltaTime)) / 1000 / 60;
  time = Math.round(time * 100) / 100;
  let chartObj = {
    charts: {
      spec: {
        id: 0,
        title: "",
        width: 400,
        height: 220,
        mark: "",
        transform: [],
        encoding: {
          column: {},
          y: {},
          x: {},
        },
        initialized: createDate(),
        timeChosen: [],
        timeClosed: [],
        deltaTime: time,
        timeSpentHovered: 0,
        data: { name: "table" }, // note: vega-lite data attribute is a plain object instead of an array
        command: command,
        pivotThis: false,
        headerFrequencyCount: headerFrequencyCount,
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
    if (extractedHeaders[i] == "cases" && intent !== "line") {
      extractedHeaders.splice(i, 1);
      i = 0;
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (extractedHeaders[i] == "date" && intent !== "line") {
      extractedHeaders.splice(i, 1);
      i = 0;
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
    options,
    headers
  );
  if (chartObj == "") {
    return chartObj;
  }
  chartObj = transform(
    data,
    filteredHeaders,
    chartObj,
    intent,
    filterFrequencyCount,
    options
  );
  chartObj.charts.spec.title = title(extractedHeaders, intent, filteredHeaders);

  return chartObj;
}

/**
 * Extract headers from the command
 * @returns
 */
function extractHeaders(command, headers, data, intent, options, chartMsg) {
  //Extract explicit headers from the command
  let doc = nlp(command);
  let extractedHeaders = [];
  for (let i = 0; i < headers.length; i++) {
    if (doc.has(headers[i].toLowerCase())) {
      extractedHeaders.push(headers[i]);
    }
  }

  //Use synonyms from the command
  if (options.useSynonyms) {
    for (let i = 0; i < chartMsg.synonymMatrix.length; i++) {
      for (let j = 0; j < chartMsg.synonymMatrix[i].length; j++) {
        if (doc.has(chartMsg.synonymMatrix[i][j].toLowerCase())) {
          extractedHeaders.push(chartMsg.synonymMatrix[i][0]);
        }
      }
    }
  }

  /**
   * Extracts headers relative to what header was spoken first
   * This is later used to recursivly iterate over the first spoken header
   */
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

  //If the intent is map, find map header in attributes
  if (intent === "map") {
    let mapFoundInExtractedHeaders = false;
    let mapFoundInDataset = false;
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "map") {
        mapFoundInExtractedHeaders = true;
      }
    }
    if (!mapFoundInExtractedHeaders) {
      for (let i = 0; i < headers.length; i++) {
        if (headers[i] == "map") {
          mapFoundInDataset = true;
          extractedHeaders.push(headers[i]);
        }
      }
    }
  }

  let dateFound = false;
  let casesFound = false;

  if (intent === "line") {
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "cases") {
        casesFound = true;
      }
      if (extractedHeaders[i] == "date") {
        dateFound = true;
      }
    }

    if (!dateFound) {
      extractedHeaders.unshift("date");
    }
    if (!casesFound) {
      extractedHeaders.unshift("cases");
    }
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i] == "cases") {
        let tmpHeader = extractedHeaders[0];
        extractedHeaders[0] = extractedHeaders[i];
        extractedHeaders[i] = tmpHeader;
      }
      if (extractedHeaders[i] == "date") {
        let tmpHeader = extractedHeaders[1];
        extractedHeaders[1] = extractedHeaders[i];
        extractedHeaders[i] = tmpHeader;
      }
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

function extractFilteredHeaders(
  command,
  data,
  headers,
  command,
  filterFrequencyCount,
  options
) {
  const headerMatrix = findFiltersInData(headers, data);
  let doc = nlp(command);
  let extractedFilteredHeaders = [];
  let foundTimeHeader = false;
  let words = command.split(" ");

  for (let i = 0; i < headerMatrix.length; i++) {
    extractedFilteredHeaders[headerMatrix[i][0]] = [];
    for (let n = 1; n < headerMatrix[i].length; n++) {
      if (doc.has(headerMatrix[i][n])) {
        extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][n]);
      } else {
        for (let j = 0; j < words.length; j++) {
          if (
            levenshtein.get(
              words[j].toLowerCase(),
              headerMatrix[i][n].toLowerCase()
            ) == 1
          ) {
            extractedFilteredHeaders[headerMatrix[i][0]].push(
              headerMatrix[i][n]
            );
          }
        }
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
  for (let i = 0; i < filterFrequencyCount.length; i++) {
    for (let j = 0; j < filterFrequencyCount[i].filters.length; j++) {
      if (findType(filterFrequencyCount[i].header, data) === "nominal") {
        if (
          filterFrequencyCount[i].filters[j].count >= options.filter.threshold
        ) {
          extractedFilteredHeaders[headerMatrix[i][0]].push(
            filterFrequencyCount[i].filters[j].filter
          );
          // chartObj.charts.spec.transform.push({
          //   filter: {
          //     field: filterFrequencyCount[i].header,
          //     oneOf: [filterFrequencyCount[i].filters[j].filter],
          //   },
          // });
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

  checkExtratedFiltersDuplicates(extractedFilteredHeaders);
  return extractedFilteredHeaders;
}

function checkDuplicates(extractedHeaders) {
  for (let i = 0; i < extractedHeaders.length; i++) {
    for (let j = i + 1; j < extractedHeaders.length; j++) {
      if (extractedHeaders[i] == extractedHeaders[j]) {
        extractedHeaders.splice(j);
        break;
      }
    }
  }
  return extractedHeaders;
}

function checkExtratedFiltersDuplicates(extractedFilteredHeaders) {
  for (let i = 0; i < extractedFilteredHeaders.length; i++) {
    for (let j = 0; j < extractedFilteredHeaders[i].length; j++) {
      for (let k = j + 1; k < extractedFilteredHeaders[i].length; k++) {
        if (extractedFilteredHeaders[i][j] == extractedFilteredHeaders[i][k]) {
          extractedFilteredHeaders[i].splice(j, 1);
        }
      }
    }
  }
  return extractedFilteredHeaders;
}