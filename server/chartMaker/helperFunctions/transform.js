const findType = require("../findType")

module.exports = (data, filteredHeaders, chartObj) => {
    let accessors = []
    let keys = Object.keys(filteredHeaders);
    for (let i = 0; i < keys.length; i++) {
        if (filteredHeaders[keys[i]].length > 0) {
            if (findType(keys[i], data) === "nominal") {
                chartObj.charts.spec.transform.push({
                    filter: { field: keys[i], oneOf: filteredHeaders[keys[i]] }
                })
            } else if (findType(keys[i], data) === "temporal") {
                chartObj.charts.spec.transform.push({
                    filter: { timeUnit: 'year', field: keys[i], range: [filteredHeaders[keys[i]][0], filteredHeaders[keys[i]][1]] }
                })
            }
        }
    }
    return chartObj
}