const findType = require("../findType");

module.exports = (chart, chartMsg, extractedFilteredValues) => {
  let accessors = [];
  let keys = Object.keys(extractedFilteredValues);
  for (let i = 0; i < keys.length; i++) {
    if (extractedFilteredValues[keys[i]].length > 0) {
      if (findType(keys[i], chartMsg.data) === "nominal") {
        chart.transform.push({
          filter: { field: keys[i], oneOf: extractedFilteredValues[keys[i]] },
        });
      } else if (findType(keys[i], chartMsg.data) === "temporal") {
        chart.transform.push({
          filter: {
            timeUnit: "year",
            field: keys[i],
            range: [
              extractedFilteredValues[keys[i]][0],
              extractedFilteredValues[keys[i]][1],
            ],
          },
        });
      }
    }
  }
  console.log(chart.transform);

  return chart;
};
