const findType = require("../findType")
const heatmap = require("../specialGraphs/heatmap")
const map = require('../specialGraphs/map')
const parallelCoordinates = require('../specialGraphs/parallelCoordinates')
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, intent, extractedHeaders, data, headerFreq, command, normalize) => {
    let numHeaders = extractedHeaders.length

    if(intent == "parallelCoordinates" || numHeaders > 3) {
        return parallelCoordinates(chartObj, extractedHeaders, data, headerFreq, command)
    }

    if(intent == "map") {
        return map(chartObj, extractedHeaders, data, headerFreq, command)
    }

    switch (numHeaders) {
        case 1:
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data),
                axis: {labelAngle: -50}
            }
            chartObj.charts.spec.encoding.y = {
                aggregate: 'count'
            }
            return chartObj
        case 2:
            extractedHeaders = findQuantitative(extractedHeaders, data, headerFreq, command, 2)
            if(extractedHeaders.length < 2) {
                chartObj.errMsg = "I tried to make a " + intent + " chart, but i coldn't find the right data"
            }
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data),
                axis: {labelAngle: -50}
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                type: findType(extractedHeaders[1], data)
            }

            if(extractedHeaders.length === 2) {
                return chartObj
            }
        case 3:
            extractedHeaders = findQuantitative(extractedHeaders, data, headerFreq, command, 3)
            extractedHeaders = reorderLowestCountForColor(extractedHeaders, data)
            chartObj.charts.spec.encoding.column = {
                field: extractedHeaders[2],
                type: findType(extractedHeaders[2], data),
                spacing: 15
            }
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data),
                axis: {labelAngle: -50}
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                type: findType(extractedHeaders[1], data)
            }
            chartObj.charts.spec.encoding.color = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data)
            }
            return chartObj
        default:
            chartObj.errMsg = "Error"
            return chartObj
    }
}

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
    let tmpHeader = extractedHeaders[targetIndex]
    extractedHeaders[targetIndex] = extractedHeaders[sourceIndex]
    extractedHeaders[sourceIndex] = tmpHeader
    return extractedHeaders
}

function findQuantitative(extractedHeaders, data, headerFreq, command, expectedHeaderLength) {
    let quantitativeFound = false;
    for(let i = 0; i < extractedHeaders.length; i++) {
        if(findType(extractedHeaders[i], data) == "temporal") {
            extractedHeaders = switchHeaders(extractedHeaders, 0, i)
        }
    }
    for (let i = 0; i < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[i], data) == "quantitative") {
            extractedHeaders = switchHeaders(extractedHeaders, 1, i)
            quantitativeFound = true
        }
    }
    if(quantitativeFound) {
        return extractedHeaders

    } else {
        return findMissing(extractedHeaders, data, expectedHeaderLength, headerFreq, command, "NQN")
    }
}


function reorderLowestCountForColor(extractedHeaders, data) {
    const uniqueLengthOne = [...new Set(data.map(item => item[extractedHeaders[0]]))];
    const uniqueLengthtwo = [...new Set(data.map(item => item[extractedHeaders[2]]))];
    if (uniqueLengthOne <= uniqueLengthtwo) {
        extractedHeaders = switchHeaders(extractedHeaders, 2, 0)

    }
    if (findType(extractedHeaders[2], data) == "quantitative") {
        extractedHeaders = switchHeaders(extractedHeaders, 2, 0)
    }

    return extractedHeaders
}
