const findType = require("../../helperFunctions/findType")

module.exports = (chartObj, intent, extractedHeaders, data) => {
    let numHeaders = extractedHeaders.length
    if (numHeaders > 3) {
        numHeaders = 3
    }

    // if(intent == "parallelCoordinates") {
    //     return parallelCoordinates(chartObj, extractedHeaders, data, headerFreq)
    // }   

    switch (numHeaders) {
        case 1:
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data)
            }
            chartObj.charts.spec.encoding.y = {
                aggregate: 'count'
            }
            return chartObj
        case 2:
            extractedHeaders = findQuantitative(extractedHeaders, data)
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data),
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                type: findType(extractedHeaders[1], data)
            }
            return chartObj
        case 3:

            extractedHeaders = findQuantitative(extractedHeaders, data)
            extractedHeaders = reorderLowestCountForColor(extractedHeaders, data)
            chartObj.charts.spec.encoding.columns = {
                field: extractedHeaders[2],
                type: findType(extractedHeaders[2], data)
            }
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                type: findType(extractedHeaders[0], data)
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                type: findType(extractedHeaders[1], data)
            }
            chartObj.charts.spec.encoding.color = {
                field: extractedHeaders[2],
                type: findType(extractedHeaders[2], data)
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

function findQuantitative(extractedHeaders, data) {
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
    return extractedHeaders
}

function createLayers(extractedHeaders, data) {
    let layers = [];
    for (let i = 0; i < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[i], data) === "quantitative") {
            let tmpHeader = extractedHeaders[0];
            extractedHeaders[0] = extractedHeaders[i];
            extractedHeaders[i] = tmpHeader;
            break;

        }
    }
    for (let i = 1; i < extractedHeaders.length; i++) {
        layers.push({
            layer: [
                {
                    mark: layerMark,
                    encoding: {
                        x: { field: extractedHeaders[i], type: findType(extractedHeaders[i], data) },
                        y: { field: extractedHeaders[0], type: findType(extractedHeaders[0], data) }

                    }
                }
            ]
        })
    }
    return layers
}


function reorderLowestCountForColor(extractedHeaders, data) {
    const uniqueLengthOne = [...new Set(data.map(item => item[extractedHeaders[0]]))];
    const uniqueLengthtwo = [...new Set(data.map(item => item[extractedHeaders[2]]))];
    if(uniqueLengthOne <= uniqueLengthtwo) {
        extractedHeaders =  switchHeaders(extractedHeaders, 2, 0)

    }
    if(findType(extractedHeaders[2], data) == "quantitative") {
        extractedHeaders = switchHeaders(extractedHeaders, 2, 0)
    }

    return extractedHeaders
}
