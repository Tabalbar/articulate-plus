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
    console.log("not found");

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
