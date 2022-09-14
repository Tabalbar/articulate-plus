/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const findType = require("./findType");
const switchHeaders = require("./switchHeaders");
const removeOtherTypes = require("./removeOtherTypes");

module.exports = (chartMsg, extractedHeaders, type) => {
  let typeFound = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == type) {
      extractedHeaders = switchHeaders(extractedHeaders, 0, i);
      extractedHeaders = removeOtherTypes(chartMsg, extractedHeaders, type);
      typeFound = true;
      break;
    }
  }

  if (!typeFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "map") {
        extractedHeaders.unshift(chartMsg.attributes[i]);
        break;
      }
    }
  }
  return {
    extractedHeaders: extractedHeaders,
    typeFound: typeFound,
  };
};
