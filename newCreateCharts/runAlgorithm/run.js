const mark = require("./specifications/mark");
const encoding = require("./specifications/encoding");
const transform = require("./specifications/transform");
const title = require("./specifications/title");
const createDate = require("../helperFunctions/createDate");

module.exports = (
  intent,
  extractedHeaders,
  data,
  headerFrequencyCount,
  command,
  options,
  filteredHeaders
) => {
  let chart = {
    spec: {
      title: "",
      width: 400,
      height: 220,
      mark: "",
      transform: [],
      encoding: {
        column: {},
        y: {},
        x: {},
      },
      initialized: createDate(),
      timeChosen: [],
      timeClosed: [],
      timeSpentHovered: 0,
      data: { name: "table" }, // note: vega-lite data attribute is a plain object instead of an array
      command: command,
      headerFrequencyCount: headerFrequencyCount,
    },
  };

  //may need in the case of extracted headers and intent don't match?
  //   for(let i = 0; i < extractedHeaders.length; i++) {
  //       if(findType(extractedHeaders[i], data) == "map" && intent !== "map") {
  //           extractedHeaders.splice(i, 1)

  //       }
  //   }
  chart = mark(chart, intent);
  chart = encoding(
    chart,
    intent,
    extractedHeaders,
    data,
    headerFrequencyCount,
    command,
    options
  );
  chartObj = transform(data, filteredHeaders, chartObj, intent);
  chartObj.charts.spec.title = title(extractedHeaders, intent, filteredHeaders);
};
