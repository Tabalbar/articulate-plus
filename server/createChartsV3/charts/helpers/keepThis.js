const findType = require("./findType");

module.exports = (chartMsg, extractedHeaders, typeToKeep) => {
  let newExtractedHeaders = [];
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == typeToKeep) {
      newExtractedHeaders.push(extractedHeaders[i]);
    }
  }

  console.log(newExtractedHeaders);
  return newExtractedHeaders;
};
