const findType = require("../../helperFunctions/findType");
const nlp = require("compromise");
const getColors = require("../../helperFunctions/covidColors");
const map = require("./charts/mapEncoding");

module.exports = (
  chart,
  intent,
  extractedHeaders,
  data,
  headerFreq,
  command,
  options,
  headers
) => {
  let numHeaders = extractedHeaders.length;
  let quantitativeFound = false;

  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], data) == "map") {
      intent = "map";
    }
  }
  if (intent == "map") {
    return map(chart, extractedHeaders, data, headerFreq, command, options);
  }

  switch (numHeaders) {
    case 1:
      chart.spec.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        axis: { labelAngle: -50, grid: false },
        sort: sortArray(extractedHeaders[0], data),
      };
      chart.spec.encoding.color = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        scale: {
          range: getColors(extractedHeaders[0]),
        },
        sort: sortArray(extractedHeaders[0], data),
      };
      chart.spec.encoding.y = {
        aggregate: "count",
      };
      return chart;
    case 2:
      quantitativeFound = findQuantitativeAndTemporal(
        extractedHeaders,
        data,
        headerFreq,
        command,
        2
      );

      if (quantitativeFound) {
        chart.spec.encoding.x = {
          field: extractedHeaders[0],
          type: findType(extractedHeaders[0], data),
          axis: { grid: false, labelAngle: -50 },
        };
        chart.spec.encoding.y = {
          field: extractedHeaders[1],
          type: findType(extractedHeaders[1], data),
          aggregate: "sum",
        };
      } else {
        chart.spec.encoding.x = {
          field: extractedHeaders[0],
          type: findType(extractedHeaders[0], data),
          axis: { labelAngle: -50, grid: false },
          sort: sortArray(extractedHeaders[0], data),
        };
        chart.spec.encoding.y = {
          field: extractedHeaders[1],
          type: findType(extractedHeaders[1], data),
          sort: sortArray(extractedHeaders[1], data),
        };
        chart.spec.encoding.color = {
          type: "quantitative",
          aggregate: "count",
          scale: { scheme: "reds" },
        };
        chart.spec.config = {
          axis: { ticks: false, labelPadding: 10, domain: false },
          view: { strokeWidth: 0 },
        };
      }

      if (extractedHeaders.length === 2) {
        return chart;
      }
      break;
    case 3:
      quantitativeFound = findQuantitativeAndTemporal(
        extractedHeaders,
        data,
        headerFreq,
        command,
        3
      );

      chart.spec.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        axis: { labelAngle: -50, title: "" },
        sort: sortArray(extractedHeaders[0], data),
        axis: { grid: false },
      };
      if (intent === "line") {
        chart.spec.encoding.y = {
          aggregate: "sum",
          field: extractedHeaders[1],
        };
      } else {
        chart.spec.encoding.y = {
          aggregate: "count",
          field: extractedHeaders[1],
        };
      }

      chart.spec.encoding.color = {
        field: extractedHeaders[2],
        type: findType(extractedHeaders[2], data),
        scale: {
          range: getColors(extractedHeaders[2]),
        },
        sort: sortArray(extractedHeaders[2], data),
      };

      return chart;

    default:
      return chart;
  }
};

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
  let tmpHeader = extractedHeaders[targetIndex];
  extractedHeaders[targetIndex] = extractedHeaders[sourceIndex];
  extractedHeaders[sourceIndex] = tmpHeader;
  return extractedHeaders;
}

function createColors(header, data) {
  let colorArray = [];
  const unique = [...new Set(data.map((item) => item[header]))];

  let colorGradient = new Rainbow();
  for (let i = 0; i < unique.length; i++) {
    colorArray.push("#" + colorGradient.colourAt(i * 20));
  }

  return colorArray;
}

function findQuantitativeAndTemporal(extractedHeaders, data) {
  let quantitativeFound = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], data) == "temporal") {
      extractedHeaders = switchHeaders(extractedHeaders, 0, i);
    }
  }
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (findType(extractedHeaders[i], data) == "quantitative") {
      extractedHeaders = switchHeaders(extractedHeaders, 1, i);
      quantitativeFound = true;
    }
  }
  return quantitativeFound;
}

function reorderLowestCountForColor(extractedHeaders, data) {
  const uniqueLengthOne = [
    ...new Set(data.map((item) => item[extractedHeaders[0]])),
  ];
  const uniqueLengthtwo = [
    ...new Set(data.map((item) => item[extractedHeaders[2]])),
  ];
  if (uniqueLengthOne <= uniqueLengthtwo) {
    extractedHeaders = switchHeaders(extractedHeaders, 2, 0);
  }
  if (findType(extractedHeaders[2], data) == "quantitative") {
    extractedHeaders = switchHeaders(extractedHeaders, 2, 0);
  }

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
