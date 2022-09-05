/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const findType = require("./findType");

module.exports = (chartMsg, extractedHeaders, typeToRemove) => {
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (extractedHeaders[i] !== undefined) {
      if (findType(extractedHeaders[i], chartMsg.data) == typeToRemove) {
        extractedHeaders.splice(i, 1);
        i = 0;
      }
    }
  }
  return extractedHeaders;
};
