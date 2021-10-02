const levenshtein = require("fast-levenshtein");

module.exports = (charts, chartMsg) => {
  let { extractedHeaders, extractedFilters } =
    extractHeadersAndFilters(chartMsg);
};

function extractHeadersAndFilters(chartMsg) {
  let words = chartMsg.command.split(" ");
  let extractedHeaders = [];
  let extractedFilters = [];
  for (let i = 0; i < chartMsg.attributes.length; i++) {
    if (command.toLowerCase().includes(chartMsg.attributes[i].toLowerCase())) {
      extractedHeaders.push(chartMsg.attributes[i]);
    }
  }
  for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    extractedFilters.push({ header: featureMatrix[i][0], filters: [] });
    for (let j = 0; j < chartMsg.featureMatrix[i].length; j++) {
      if (
        chartMsg
          .toLowerCase()
          .includes(chartMsg.featureMatrix[i][j].toLowerCase())
      ) {
        extractedFilters[i].filters.push(chartMsg.featureMatrix[i][j]);
      }
    }
  }
}
