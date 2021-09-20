const findType = require("../../../helperFunctions/findType");
const findMissing = require("../../../helperFunctions/findMissing").findMissing;
const nlp = require("compromise");
const getColors = require("../../../helperFunctions/covidColors");

module.exports = (chart, extractedHeaders, data) => {
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
  chart.spec.projection = { type: "albersUsa" };
  chart.spec.encoding = {
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
      sort: sortArray(extractedHeaders[1], data),
    },
  };
  return chart;
};

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
  let tmpHeader = extractedHeaders[targetIndex];
  extractedHeaders[targetIndex] = extractedHeaders[sourceIndex];
  extractedHeaders[sourceIndex] = tmpHeader;
  return extractedHeaders;
}

function sortArray(header, data) {
  let order = [];
  const unique = [...new Set(data.map((item) => item[header]))];
  if (unique.length == 5) {
    for (let i = 0; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("very high")) {
        switchHeaders(unique, 0, i);
        break;
      }
    }

    for (let i = 1; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("high")) {
        switchHeaders(unique, 1, i);
        break;
      }
    }

    for (let i = 2; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("moderate") || doc.has("medium")) {
        switchHeaders(unique, 2, i);
        break;
      }
    }

    for (let i = 3; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("low")) {
        switchHeaders(unique, 3, i);
        break;
      }
    }

    for (let i = 4; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("very low")) {
        switchHeaders(unique, 4, i);
        break;
      }
    }
  }
  if (unique.length == 4) {
    for (let i = 0; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("high")) {
        switchHeaders(unique, 0, i);
        break;
      }
    }

    for (let i = 1; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("moderate") || doc.has("medium")) {
        switchHeaders(unique, 1, i);
        break;
      }
    }

    for (let i = 2; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("low")) {
        switchHeaders(unique, 2, i);
        break;
      }
    }

    for (let i = 3; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("very low")) {
        switchHeaders(unique, 3, i);
        break;
      }
    }
  }

  return unique;
}
