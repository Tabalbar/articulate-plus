const findType = require("./findType");

module.exports = (chartMsg, extractedHeaders, typeToRemove) => {
  for (let i = 1; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], chartMsg.data) == typeToRemove) {
      extractedHeaders.splice(i, 1);
      i = 1;
    }
  }
  return extractedHeaders;
};
