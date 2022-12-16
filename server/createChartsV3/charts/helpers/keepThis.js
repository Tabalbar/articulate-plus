/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const findType = require("./findType");

module.exports = (chartMsg, extractedHeaders, typeToKeep) => {
  let newExtractedHeaders = [];
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == typeToKeep) {
      newExtractedHeaders.push(extractedHeaders[i]);
    }
  }

  return newExtractedHeaders;
};
