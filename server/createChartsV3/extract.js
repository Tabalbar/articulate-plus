const nlp = require("compromise");
const levenshtein = require("fast-levenshtein");
const findType = require("./charts/helpers/findType");

module.exports = {
  headers: (chartMsg, headerFrequencyCount, options) => {
    // const result1 = str.replace(/foo/g, "moo");

    chartMsg.command = chartMsg.command.replace(/_/g, " ");
    //Extract explicit headers from the command
    let doc = nlp(chartMsg.command);
    let extractedHeaders = [];
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (
        doc.has(chartMsg.attributes[i].toLowerCase()) ||
        doc.has(chartMsg.attributes[i].toLowerCase() + "s")
      ) {
        extractedHeaders.push(chartMsg.attributes[i]);
      }
    }
    //Use synonyms from the command
    if (options.useSynonyms) {
      for (let i = 0; i < chartMsg.synonymMatrix.length; i++) {
        for (let j = 1; j < chartMsg.synonymMatrix[i].length; j++) {
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
        index: chartMsg.command.indexOf(extractedHeaders[i].toLowerCase()),
        header: extractedHeaders[i],
      });
    }
    wordPosition.sort((a, b) => a.index - b.index);
    extractedHeaders = [];
    for (let i = 0; i < wordPosition.length; i++) {
      extractedHeaders.push(wordPosition[i].header);
    }
    //Using overhearing to extract headers
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
      for (let i = 0; i < sortedHeaders.length; i++) {
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

    //Delete any duplicates in headers
    extractedHeaders = checkDuplicates(extractedHeaders);
    return extractedHeaders;
  },

  filterValues: (chartMsg, filterFrequencyCount, options) => {
    chartMsg.command = chartMsg.command.replace(/ /g, "-");
    // let doc = nlp(chartMsg.command);
    let extractedFilteredHeaders = [];
    // let foundTimeHeader = false;
    let words = chartMsg.command.split("-");
    //Extract explicit filters used
    // for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    //   extractedFilteredHeaders[chartMsg.featureMatrix[i][0]] = [];
    //   for (let n = 1; n < chartMsg.featureMatrix[i].length; n++) {
    //     if (doc.has(chartMsg.featureMatrix[i][n])) {
    //       extractedFilteredHeaders[chartMsg.featureMatrix[i][0]].push(
    //         chartMsg.featureMatrix[i][n]
    //       );
    //     } else {
    //       for (let j = 0; j < words.length; j++) {
    //         if (
    //           levenshtein.get(
    //             words[j].toLowerCase(),
    //             chartMsg.featureMatrix[i][n].toLowerCase()
    //           ) == 1
    //         ) {
    //           extractedFilteredHeaders[chartMsg.featureMatrix[i][0]].push(
    //             chartMsg.featureMatrix[i][n]
    //           );
    //         }
    //       }
    //     }
    //   }
    // }
    for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
      extractedFilteredHeaders[chartMsg.featureMatrix[i][0]] = [];
      for (let n = 1; n < chartMsg.featureMatrix[i].length; n++) {
        if (chartMsg.command.includes(chartMsg.featureMatrix[i][n])) {
          extractedFilteredHeaders[chartMsg.featureMatrix[i][0]].push(
            chartMsg.featureMatrix[i][n]
          );
        } else {
          for (let j = 0; j < words.length; j++) {
            if (
              levenshtein.get(
                words[j].toLowerCase(),
                chartMsg.featureMatrix[i][n].toLowerCase()
              ) == 1
            ) {
              extractedFilteredHeaders[chartMsg.featureMatrix[i][0]].push(
                chartMsg.featureMatrix[i][n]
              );
            }
          }
        }
      }
    }

    //Extract filters based on overhearing
    for (let i = 0; i < filterFrequencyCount.length; i++) {
      for (let j = 0; j < filterFrequencyCount[i].filters.length; j++) {
        if (
          findType(filterFrequencyCount[i].header, chartMsg.data) === "nominal"
        ) {
          if (
            filterFrequencyCount[i].filters[j].count >= options.filter.threshold
          ) {
            extractedFilteredHeaders[chartMsg.featureMatrix[i][0]].push(
              filterFrequencyCount[i].filters[j].filter
            );
          }
        }
      }
    }
    //turn command back
    chartMsg.command = chartMsg.command.replace(/-/g, " ");

    //delete any duplciates
    checkExtratedFiltersDuplicates(extractedFilteredHeaders);
    return extractedFilteredHeaders;
  },
};

function checkDuplicates(extractedHeaders) {
  let j = 0;
  for (let i = 0; i < extractedHeaders.length; i++) {
    for (j = i + 1; j < extractedHeaders.length; j++) {
      if (extractedHeaders[i] == extractedHeaders[j] && i !== j) {
        extractedHeaders.splice(j, 1);
        j = 0;
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
