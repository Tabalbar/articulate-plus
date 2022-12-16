/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const findType = require("./findType");
const switchHeaders = require("./switchHeaders");

module.exports = (chartMsg, extractedHeaders) => {
  let typeFound = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == "quantitative") {
      extractedHeaders = switchHeaders(extractedHeaders, 0, i);
      typeFound = true;
      break;
    }
  }

  if (!typeFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (findType(chartMsg.attributes[i], chartMsg.data) == "quantitative") {
        extractedHeaders.unshift(chartMsg.attributes[i]);
        typeFound = true;
        break;
      }
    }
  }
  return {
    extractedHeaders: extractedHeaders,
    typeFound: typeFound,
  };
};
