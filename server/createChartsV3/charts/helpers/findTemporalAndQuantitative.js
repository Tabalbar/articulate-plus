const findType = require("./findType");
const switchHeaders = require("./switchHeaders");

module.exports = (chartMsg, extractedHeaders, options) => {
  let quantitativeFound = false;
  let temporalFound = false;
  if (extractedHeaders.length < 2) {
    return false;
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "map") {
      extractedHeaders.splice(i, 1);
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "temporal") {
      temporalFound = true;
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "quantitative") {
      quantitativeFound = true;
    }
  }
  if (!temporalFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "temporal") {
        temporalFound = true;
        extractedHeaders.unshift(chartMsg.attributes[i]);
      }
    }
  }
  if (!quantitativeFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "quantitative") {
        quantitativeFound = true;
        extractedHeaders.unshift(chartMsg.attributes[i]);
      }
    }
  }

  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "quantitative") {
      switchHeaders(extractedHeaders, 1, i);
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "temporal") {
      switchHeaders(extractedHeaders, 0, i);
    }
  }

  return {
    extractedHeaders: extractedHeaders,
    quantitativeFound: quantitativeFound,
    temporalFound: temporalFound,
  };
};
