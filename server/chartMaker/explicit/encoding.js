const findType = require("../findType")
const lineBar = require('./marks/lineBar')
const parallelCoordinates = require('../specialGraphs/parallelCoordinates')
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, intent, extractedHeaders, data) => {
    let numHeaders = extractedHeaders.length
    // if (numHeaders > 3) {
    //     numHeaders = 4
    // }
    if(intent == "line" || intent == "bar") {
        chartObj = lineBar(chartObj, intent, extractedHeaders, data);
    }
    return chartObj
    // if(intent == "parallelCoordinates") {
    //     return parallelCoordinates(chartObj, extractedHeaders, data, headerFreq)
    // }

    // switch (numHeaders) {
    //     case 1:
    //         chartObj.charts.spec.encoding.x = {
    //             field: extractedHeaders[0],
    //             type: findType(extractedHeaders[0], data)
    //         }
    //         chartObj.charts.spec.encoding.y = {
    //             aggregate: 'count'
    //         }
    //         return chartObj
    //     case 2:
    //         extractedHeaders = findQuantitative(extractedHeaders, data, headerFreq)
    //         chartObj.charts.spec.encoding.x = {
    //             field: extractedHeaders[0],
    //             type: findType(extractedHeaders[0], data),
    //         }
    //         chartObj.charts.spec.encoding.y = {
    //             field: extractedHeaders[1],
    //             type: findType(extractedHeaders[1], data)
    //         }
    //         return chartObj
    //     case 3:
    //         extractedHeaders = findQuantitative(extractedHeaders, data, headerFreq)
    //         chartObj.charts.spec.encoding.columns = {
    //             field: extractedHeaders[2],
    //             type: findType(extractedHeaders[2], data)
    //         }
    //         chartObj.charts.spec.encoding.x = {
    //             field: extractedHeaders[0],
    //             type: findType(extractedHeaders[0], data)
    //         }
    //         chartObj.charts.spec.encoding.y = {
    //             field: extractedHeaders[1],
    //             type: findType(extractedHeaders[1], data)
    //         }
    //         chartObj.charts.spec.encoding.color = {
    //             field: extractedHeaders[2],
    //             type: findType(extractedHeaders[2], data)
    //         }
    //         return chartObj
    //     case 4:
    //         chartObj.charts.spec.columns = extractedHeaders.length - 1
    //         chartObj.charts.spec.concat = createLayers(extractedHeaders, data)
    //         delete chartObj.charts.spec.encoding
    //         return chartObj
    //     default:
    //         chartObj.errMsg = "Error"
    //         return chartObj
    // }
}
