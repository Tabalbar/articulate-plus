const findType = require("../findType")
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, extractedHeaders, data, headerFreq, command, normalize, intent) => {
    extractedHeaders = findMissing(extractedHeaders, data, 3, headerFreq, command, "NQT")
    if(extractedHeaders.length !== 3) {
        chartObj.errMsg = "I tried to make a stacked bar chart but I don't have the right data for it."
    }
    for(let i = 0; i < extractedHeaders.length; i++) {
        if(findType(extractedHeaders[i], data) == "nominal") {
            let tmpHeader = extractedHeaders[0]
            extractedHeaders[0] = extractedHeaders[i]
            extractedHeaders[i] = tmpHeader
        }
    }
    for(let i = 1; i < extractedHeaders.length; i++) {
        if(findType(extractedHeaders[i], data) == "quantitative") {
            let tmpHeader = extractedHeaders[1]
            extractedHeaders[1] = extractedHeaders[i]
            extractedHeaders[i] = tmpHeader
        }
    }
    for(let i = 2; i < extractedHeaders.length; i++) {
        if(findType(extractedHeaders[i], data) == "temporal") {
            let tmpHeader = extractedHeaders[2]
            extractedHeaders[2] = extractedHeaders[i]
            extractedHeaders[i] = tmpHeader
        }
    }
    if(intent == "stackedBar") {
        chartObj.charts.spec.mark = { type: "bar", cornerRadiusTopLeft: 3, cornerRadiusTopRight: 3 }

    } else if(intent == "lineArea") {
        chartObj.charts.spec.mark = "area"
    }

    chartObj.charts.spec.encoding.x = {
        timeUnit: "yearmonth",
        field: extractedHeaders[2]
    }

    if(normalize) {
        chartObj.charts.spec.encoding.y = {
            aggregate: "sum",
            field: extractedHeaders[1],
            stack: "normalize"
        }
    } else {
        chartObj.charts.spec.encoding.y = {
            aggregate: "sum",
            field: extractedHeaders[1]
        }
    }

    chartObj.charts.spec.encoding.color = {
        field: extractedHeaders[0]
    }
    return chartObj
}