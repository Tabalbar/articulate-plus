const nlp = require("compromise");
const findType = require("../helperFunctions/findType");
const Sentiment = require("sentiment");
const countHeaderFrequency = require("./countHeaderFrequency");

const allIntents = ["heatmap", "line", "bar", "map"];

//Used inside extractHeaders method
const randomNumber = require("../helperFunctions/randomNumber");

module.exports = class ChartInfo {
  extractedHeaders = [];

  constructor(chartMsg, options, intent) {
    this.headers = chartMsg.attributes;
    this.command = chartMsg.command;
    this.data = chartMsg.data;
    this.transcript = chartMsg.transcript;
    this.synonymMatrix = chartMsg.synonymMatrix;
    this.featureMatrix = chartMsg.featureMatrix;
    this.options = options;
    this.headerFrequencyCount = countHeaderFrequency(
      chartMsg.transcript,
      chartMsg.featureMatrix,
      chartMsg.synonymMatrix,
      chartMsg.data,
      options
    );
    this.intent = intent;
  }

  extractHeaders() {
    //Extract explicit headers from the command
    let doc = nlp(this.command);
    let extractedHeaders = [];
    const thresholdValue = options.threshold;
    let maxLengthOfIntents = allIntents.length;

    for (let i = 0; i < this.headers.length; i++) {
      if (doc.has(this.headers[i].toLowerCase())) {
        extractedHeaders.push(this.headers[i]);
      }
    }

    //Use synonyms from the command
    if (this.options.useSynonyms) {
      for (let i = 0; i < this.synonymMatrix.length; i++) {
        for (let j = 0; j < this.synonymMatrix[i].length; j++) {
          if (doc.has(this.synonymMatrix[i][j].toLowerCase())) {
            this.extractedHeaders.push(this.synonymMatrix[i][0]);
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
        index: this.command.indexOf(extractedHeaders[i].toLowerCase()),
        header: extractedHeaders[i],
      });
    }
    wordPosition.sort((a, b) => a.index - b.index);
    extractedHeaders = [];
    for (let i = 0; i < wordPosition.length; i++) {
      extractedHeaders.push(wordPosition[i].header);
    }

    //Back Filling with most spoken attribute on a threshold
    if (this.options.window.toggle) {
      const headerKeys = Object.keys(this.headerFrequencyCount);
      let headersToSort = [];
      for (let i = 0; i < headerKeys.length; i++) {
        for (
          let j = 0;
          j < this.headerFrequencyCount[headerKeys[i]].length;
          j++
        ) {
          headersToSort.push(this.headerFrequencyCount[headerKeys[i]][j]);
        }
      }
      let sortedHeaders = headersToSort.sort((a, b) =>
        a.count < b.count ? 1 : -1
      );
      //**POSSIBLE BUG INDEX OUT OF RANGE**.
      for (let i = 0; i < 4; i++) {
        if (sortedHeaders[i].count >= thresholdValue) {
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

    //If the intent is map, find map header in attributes
    if (this.intent === "map") {
      let mapFoundInExtractedHeaders = false;
      let mapFoundInDataset = false;
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == "map") {
          mapFoundInExtractedHeaders = true;
          mapFoundInDataset = true;
        }
      }
      if (!mapFoundInExtractedHeaders) {
        for (let i = 0; i < this.headers.length; i++) {
          if (this.headers[i] == "map") {
            mapFoundInDataset = true;
            extractedHeaders.push(headers[i]);
          }
        }
      }

      if (mapFoundInDataset || mapFoundInExtractedHeaders) {
        for (let i = 0; i < extractedHeaders.length; i++) {
          if (findType(extractedHeaders[i], data) == "map") {
            let tmpHeader = extractedHeaders[0];
            extractedHeaders[0] = extractedHeaders[i];
            extractedHeaders[i] = tmpHeader;
          }
        }
      }

      //If no date or quantitative found, Need to change intent.
      //Rerun extractHeaders with new intent
      if (!mapFoundInDataset) {
        this.intent = Math.floor(Math.random() * maxLengthOfIntents);
        this.extractHeaders(
          this.command,
          this.headers,
          this.data,
          intent,
          this.options,
          this.synonymMatrix
        );
      }
    }

    if (this.intent === "line") {
      let dateFound = false;
      let quantitativeFound = false;
      let dateFoundInDataset = false;
      let quantitativeFoundInDataset = false;

      for (let i = 0; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == "date") {
          dateFound = true;
          dateFoundInDataset = true;
        }
        if (findType(extractedHeaders[i], this.data) == "quantitative") {
          quantitativeFound = true;
          quantitativeFoundInDataset = true;
        }
      }

      if (!dateFound) {
        for (let i = 0; i < headers.length; i++) {
          if (findType(extractedHeaders[i], this.data) == "temporal") {
            extractedHeaders.unshift(extractedHeaders[i]);
            dateFoundInDataset = true;
            break;
          }
        }
      }
      if (!quantitativeFound) {
        for (let i = 0; i < headers.length; i++) {
          if (findType(extractedHeaders[i], this.data) == "quantitative") {
            quantitativeFoundInDataset = true;
            extractedHeaders.unshift(extractedHeaders[i]);
            break;
          }
        }
      }

      //If no date or quantitative found, Need to change intent.
      //Rerun extractHeaders with new intent
      if (!dateFoundInDataset || !quantitativeFoundInDataset) {
        intent = Math.floor(Math.random() * maxLengthOfIntents);

        this.extractHeaders(
          this.command,
          this.headers,
          this.data,
          intent,
          this.options,
          this.chartMsg
        );
      }

      for (let i = 0; i < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[i], this.data) == "quantitative") {
          let tmpHeader = extractedHeaders[0];
          extractedHeaders[0] = extractedHeaders[i];
          extractedHeaders[i] = tmpHeader;
        }
        if (findType(extractedHeaders[i], this.data) == "temporal") {
          let tmpHeader = extractedHeaders[1];
          extractedHeaders[1] = extractedHeaders[i];
          extractedHeaders[i] = tmpHeader;
        }
      }
    }

    //check if enough headers to create a heatmap
    if (intent == "heatmap") {
      let nominalOrQuantitative1Found = false;
      let nominalOrQuantitative2Found = false;
      let nominalOrQuantitative1FoundInDataset = false;
      let nominalOrQuantitative2FoundInDataset = false;
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (
          findType(extractedHeaders[i], this.data) == "nominal" ||
          findType(extractedHeaders[i], this.data) == "quantitative"
        ) {
          nominalOrQuantitative1Found = true;
        }
      }
      for (let i = 1; i < extractedHeaders.length; i++) {
        if (
          findType(extractedHeaders[i], this.data) == "nominal" ||
          findType(extractedHeaders[i], this.data) == "quantitative"
        ) {
          nominalOrQuantitative2Found = true;
        }
      }
      //If not found in extractedHeaders. find them
      if (!nominalOrQuantitative2Found) {
        for (let i = 0; i < this.headers.length; i++) {
          if (
            findType(this.headers[i], this.data) == "nominal" ||
            findType(this.headers[i], this.data) == "quantitative"
          ) {
            let isDuplicate = false;
            for (let i = 0; i < extractedHeaders.length; i++) {
              if (extractedHeaders[i] == this.headers) {
                isDuplicate = true;
                break;
              }
            }
            if (!isDuplicate) {
              nominalOrQuantitative2FoundInDataset = true;
              extractedHeaders.push(extractedHeaders[i]);
              break;
            }
          }
        }
      }
      if (!nominalOrQuantitative1Found) {
        for (let i = 0; i < this.headers.length; i++) {
          if (
            findType(extractedHeaders[0], this.data) == "nominal" ||
            findType(extractedHeaders[i], this.data) == "quantitative"
          ) {
            let isDuplicate = false;
            for (let i = 0; i < extractedHeaders.length; i++) {
              if (extractedHeaders[i] == this.headers) {
                isDuplicate = true;
                break;
              }
            }
            if (!isDuplicate) {
              nominalOrQuantitative2FoundInDataset = true;
              extractedHeaders.push(extractedHeaders[i]);
              break;
            }
          }
        }
      }

      if (
        !nominalOrQuantitative1FoundInDataset ||
        !nominalOrQuantitative2FoundInDataset
      ) {
        intent = Math.floor(Math.random() * maxLengthOfIntents);

        this.extractHeaders(
          this.command,
          this.headers,
          this.data,
          intent,
          this.options,
          this.chartMsg
        );
      }
    }

    //Check for duplicates
    for (let i = 0; i < extractedHeaders.length; i++) {
      for (let j = i + 1; j < extractedHeaders.length; j++) {
        if (extractedHeaders[i] == extractedHeaders[j]) {
          extractedHeaders.splice(j, 1);
          break;
        }
      }
    }

    return extractedHeaders;
  }

  extractFilteredHeaders() {
    let filterMatrix = [];
    for (let i = 0; i < this.headers.length; i++) {
      if (findType(this.headers[i], this.data) === "nominal") {
        var flags = [],
          output = [this.headers[i]],
          l = this.data.length,
          n;
        for (n = 0; n < l; n++) {
          if (flags[this.data[n][this.headers[i]]]) continue;
          flags[this.data[n][this.headers[i]]] = true;
          output.push(this.data[n][this.headers[i]]);
        }
        filterMatrix.push(output);
      } else {
        filterMatrix.push([this.headers[i]]);
      }
    }
    let doc = nlp(this.command);
    let extractedFilteredHeaders = [];
    let foundTimeHeader = false;
    for (let i = 0; i < filterMatrix.length; i++) {
      extractedFilteredHeaders[filterMatrix[i][0]] = [];
      for (let n = 1; n < filterMatrix[i].length; n++) {
        if (doc.has(filterMatrix[i][n])) {
          extractedFilteredHeaders[filterMatrix[i][0]].push(filterMatrix[i][n]);
        }
      }

      if (
        findType(filterMatrix[i][0], this.data) === "temporal" &&
        !foundTimeHeader
      ) {
        const { foundTime, timeHeader } = extractHeadersWithoutFilter(
          doc,
          this.headers,
          this.data,
          this.command
        );
        if (!foundTime) {
          findDates(doc, extractedFilteredHeaders[filterMatrix[i][0]]);
          this.command += " " + filterMatrix[i][0];
          foundTimeHeader = true;
        } else {
          if (timeHeader === filterMatrix[i][0]) {
            findDates(doc, extractedFilteredHeaders[filterMatrix[i][0]]);
          }
        }
      }
    }

    function findDates(docCommand, extractedFilteredHeaders) {
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
          extractedFilteredHeaders.push(yearBefore);
          extractedFilteredHeaders.push(yearAfter);
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
    return extractedFilteredHeaders;
  }
};
