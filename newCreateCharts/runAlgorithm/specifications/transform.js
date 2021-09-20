const findType = require("../helperFunctions/findType");

module.exports = (data, filteredHeaders, chart, intent) => {
  let accessors = [];
  let keys = Object.keys(filteredHeaders);
  for (let i = 0; i < keys.length; i++) {
    if (filteredHeaders[keys[i]].length > 0) {
      if (findType(keys[i], data) === "nominal") {
        chart.spec.transform.push({
          filter: { field: keys[i], oneOf: filteredHeaders[keys[i]] },
        });
      } else if (findType(keys[i], data) === "temporal") {
        chart.spec.transform.push({
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
    chart.spec.transform.push({
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
      data: chart.spec.data,
      mark: chart.spec.mark,
      transform: chart.spec.transform,
      encoding: chart.spec.encoding,
    };
    delete chart.spec.data;
    delete chart.spec.mark;
    delete chart.spec.transform;
    delete chart.spec.encoding;
    delete chart.spec.concat;
    chart.spec.layer = [
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

  return chart;
};
