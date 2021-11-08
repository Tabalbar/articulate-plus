const findType = require("./findType");

module.exports = (chartMsg, extractedHeaders, typeToRemove) => {
  for (let i = 0; i < extractedHeaders.length; i++) {
    console.log(extractedHeaders[i]);
    if (extractedHeaders[i] !== undefined) {
      if (findType(extractedHeaders[i], chartMsg.data) == typeToRemove) {
        extractedHeaders.splice(i, 1);
        i = 0;
        console.log("removed");
      }
      // console.log(extractedHeaders[i]);
    }
  }
  return extractedHeaders;
};
