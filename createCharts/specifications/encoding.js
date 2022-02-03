const findType = require("../helperFunctions/findType");
const map = require("../charts/map");
const parallelCoordinates = require("../charts/parallelCoordinates");
const nlp = require("compromise");
const getColors = require("../static/CovidColors");
const getSort = require("../static/CovidSort");

module.exports = (
  chartObj,
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
    if (extractedHeaders[i] == "map") {
      intent = "map";
    }
  }
  if (intent == "map") {
    return map(chartObj, extractedHeaders, data, headerFreq, command, options);
  }

  switch (numHeaders) {
    case 1:
      chartObj.charts.spec.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        axis: { labelAngle: -50, grid: false },
        sort: getSort(extractedHeaders[0], data),
      };
      chartObj.charts.spec.encoding.color = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        scale: {
          range: getColors(extractedHeaders[0]),
        },
        sort: getSort(extractedHeaders[0], data),
      };
      chartObj.charts.spec.encoding.y = {
        aggregate: "count",
        title: "Number of Counties",
      };
      return chartObj;
    case 2:
      quantitativeFound = findQuantitative(
        extractedHeaders,
        data,
        headerFreq,
        command,
        2
      );
      if (intent == "bar") {
        chartObj.charts.spec.mark = "rect";
      }
      if (extractedHeaders.length < 2) {
        chartObj.errMsg =
          "I tried to make a " +
          intent +
          " chart, but i coldn't find the right data";
      }

      if (quantitativeFound) {
        chartObj.charts.spec.encoding.x = {
          field: extractedHeaders[0],
          type: findType(extractedHeaders[0], data),
          axis: { grid: false, labelAngle: -50 },
        };
        chartObj.charts.spec.encoding.y = {
          field: extractedHeaders[1],
          type: findType(extractedHeaders[1], data),
          aggregate: "sum",
        };
      } else {
        chartObj.charts.spec.encoding.x = {
          field: extractedHeaders[0],
          type: findType(extractedHeaders[0], data),
          axis: { labelAngle: -50, grid: false },
          sort: getSort(extractedHeaders[0], data),
        };
        chartObj.charts.spec.encoding.y = {
          field: extractedHeaders[1],
          type: findType(extractedHeaders[1], data),
          sort: getSort(extractedHeaders[1], data),
        };
        chartObj.charts.spec.encoding.color = {
          type: "quantitative",
          aggregate: "count",
          scale: { scheme: "reds" },
        };
        chartObj.charts.spec.config = {
          axis: { ticks: false, labelPadding: 10, domain: false },
          view: { strokeWidth: 0 },
        };
      }

      if (extractedHeaders.length === 2) {
        return chartObj;
      }
      break;
    case 3:
      quantitativeFound = findQuantitative(
        extractedHeaders,
        data,
        headerFreq,
        command,
        3
      );
      chartObj.charts.spec.encoding.x = {
        field: extractedHeaders[0],
        type: findType(extractedHeaders[0], data),
        axis: { labelAngle: -50, title: "" },
        sort: getSort(extractedHeaders[0], data),
        axis: { grid: false },
      };
      if (intent === "line") {
        chartObj.charts.spec.encoding.y = {
          aggregate: "sum",
          field: extractedHeaders[1],
        };
      } else {
        chartObj.charts.spec.encoding.y = {
          aggregate: "count",
          field: extractedHeaders[1],
        };
      }

      // chartObj.charts.spec.encoding.column = {
      //   field: extractedHeaders[1],
      //   type: findType(extractedHeaders[1], data),
      //   sort: getSort(extractedHeaders[1], data),
      //   spacing: 40,
      // };
      chartObj.charts.spec.encoding.color = {
        field: extractedHeaders[2],
        type: findType(extractedHeaders[2], data),
        scale: {
          range: getColors(extractedHeaders[2]),
        },
        sort: getSort(extractedHeaders[2], data),
      };

      return chartObj;

    default:
      chartObj = "";
      return chartObj;
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

function findQuantitative(
  extractedHeaders,
  data,
  headerFreq,
  command,
  expectedHeaderLength
) {
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
