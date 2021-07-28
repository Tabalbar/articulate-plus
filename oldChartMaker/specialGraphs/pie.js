const findType = require("../findType")
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, extractedHeaders, data, headerFreq, command) => {
    if(extractedHeaders.length == 0) {
        extractedHeaders =  findMissing(extractedHeaders, data, 1, headerFreq, command, "NQT")
    }
    for (let i = 0; 0 < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[0], data) == "nominal") {
            chartObj.charts.spec.encoding.theta = { aggregate: "count" }
            chartObj.charts.spec.encoding.color = { field: extractedHeaders[i], type: findType(extractedHeaders[i], data) }
            return chartObj

        }
    }

}