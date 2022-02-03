const findType = require("../helperFunctions/findType");
const findMissing = require("../helperFunctions/findMissing").findMissing;
const nlp = require("compromise");
const getColors = require("../static/CovidColors");
const getSort = require("../static/CovidSort");

module.exports = (
  chartObj,
  extractedHeaders,
  data,
  headerFreq,
  command,
  options
) => {
  chartObj.charts.spec.projection = { type: "albersUsa" };
  extractedHeaders = findAndAddMapAttribute(extractedHeaders);

  if (extractedHeaders.length < 2) {
    extractedHeaders = findMissing(
      extractedHeaders,
      data,
      2,
      headerFreq,
      command,
      "MN"
    );
  }
  if (extractedHeaders == "") {
    return "";
  }

  if (extractedHeaders[0] !== "map") {
    extractedHeaders = switchHeaders(
      extractedHeaders,
      0,
      extractedHeaders.length - 1
    );
  }
  chartObj.charts.spec.encoding = {
    shape: {
      field: "geo",
      type: "geojson",
    },
    color: {
      field: extractedHeaders[1],
      type: findType(extractedHeaders[1], data),
      scale: {
        range: getColors(extractedHeaders[1]),
      },
      sort: getSort(extractedHeaders[1], data),
    },
  };
  return chartObj;
};

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
  let tmpHeader = extractedHeaders[targetIndex];
  extractedHeaders[targetIndex] = extractedHeaders[sourceIndex];
  extractedHeaders[sourceIndex] = tmpHeader;
  return extractedHeaders;
}

function findAndAddMapAttribute(extractedHeaders) {
  let mapFound = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (extractedHeaders[i] === "map") {
      mapFound = true;
      if (i > 0) {
        extractedHeaders = switchHeaders(
          extractedHeaders,
          0,
          extractedHeaders.length - 1
        );
      }
      break;
    }
  }
  if (!mapFound) {
    extractedHeaders.push("map");

    extractedHeaders = switchHeaders(
      extractedHeaders,
      0,
      extractedHeaders.length - 1
    );
  }
  return extractedHeaders;
}
