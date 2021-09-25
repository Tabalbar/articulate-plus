const findType = require("../chartMaker/findType");

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
  }

  return chartObj;
};
