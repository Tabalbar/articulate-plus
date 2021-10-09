const findType = require("./findType");
const switchHeaders = require("./switchHeaders");

module.exports = (chartMsg, extractedHeaders, options) => {
  let quantitativeFound = false;
  let temporalFound = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "temporal") {
      temporalFound = true;
      switchHeaders(extractedHeaders, 0, i);
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "quantitative") {
      quantitativeFound = true;
      switchHeaders(extractedHeaders, 1, i);
    }
  }
  if (!temporalFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "temporal") {
        temporalFound = true;
        extractedHeaders.unshift(chartMsg.attributes[i]);
        switchHeaders(extractedHeaders, 0, 0);
      }
    }
  }
  if (!quantitativeFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "quantitative") {
        quantitativeFound = true;
        extractedHeaders.unshift(chartMsg.attributes[i]);

        switchHeaders(extractedHeaders, 1, 0);
      }
    }
  }

  return {
    extractedHeaders: extractedHeaders,
    quantitativeFound: quantitativeFound,
    temporalFound: temporalFound,
  };
};
