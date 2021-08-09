const findType = require("../helperFunctions/findType");

module.exports = (data, filteredHeaders, chartObj, intent) => {
  let accessors = [];
  let keys = Object.keys(filteredHeaders);
  for (let i = 0; i < keys.length; i++) {
    if (filteredHeaders[keys[i]].length > 0) {
      if (findType(keys[i], data) === "nominal") {
        chartObj.charts.spec.transform.push({
          filter: { field: keys[i], oneOf: filteredHeaders[keys[i]] },
        });
      } else if (findType(keys[i], data) === "temporal") {
        chartObj.charts.spec.transform.push({
          filter: {
            timeUnit: "year",
            field: keys[i],
            range: [filteredHeaders[keys[i]][0], filteredHeaders[keys[i]][1]],
          },
        });
      }
    }
  }
  if (intent == "map") {
    chartObj.charts.spec.transform.push({
      lookup: "map",
      from: {
        data: {
          url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
          format: { type: "topojson", feature: "counties" },
        },
        key: "id",
      },
      as: "geo",
    });
    let obj = {
      data: chartObj.charts.spec.data,
      mark: chartObj.charts.spec.mark,
      transform: chartObj.charts.spec.transform,
      encoding: chartObj.charts.spec.encoding,
    };
    delete chartObj.charts.spec.data;
    delete chartObj.charts.spec.mark;
    delete chartObj.charts.spec.transform;
    delete chartObj.charts.spec.encoding;
    delete chartObj.charts.spec.concat;
    chartObj.charts.spec.layer = [
      {
        data: {
          url: "https://raw.githubusercontent.com/vega/vega/master/docs/data/us-10m.json",
          format: {
            type: "topojson",
            feature: "states",
          },
        },
        mark: {
          type: "geoshape",
          fill: "lightgray",
          stroke: "white",
        },
      },
      obj,
    ];
  }

  return chartObj;
};
