const findMissing = require('../findMissing').findMissing
const findType = require('../findType')

module.exports = (actualCommand, extractedHeaders, filteredHeaders, data, headerFreq, command) => {
    if (extractedHeaders.length > 2) {
        let chartObj = {
            errmsg: "I tried to make a radar graph. Try again with less attributes."
        }
        return chartObj
    } else if (extractedHeaders.length < 2) {
        extractedHeaders = findMissing(extractedHeaders, data, 2, headerFreq, command, "NQT")
    }
    for (let i = 0; i < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[i], data) == "nominal") {
            switchHeaders(extractedHeaders, 0, i)
        }
        if (findType(extractedHeaders[i], data) == "quantitative") {
            switchHeaders(extractedHeaders, 1, i)
        }
    }
    let chartObj = {
        plotly: true,
        data: [{
            r: extractedHeaders[1],
            theta: extractedHeaders[0],
            fill: 'toself'
        }],
        layout: {
            polar: {
                redialaxis: {
                    visible: true,
                    range: [Math.min(extractedHeaders[1]), Math.max(extractedHeaders[1])]
                }
            },
            title: { text: actualCommand }
        }
    }
    return chartObj
}

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
    let tmpHeader = extractedHeaders[targetIndex]
    extractedHeaders[targetIndex] = extractedHeaders[sourceIndex]
    extractedHeaders[sourceIndex] = tmpHeader
    return extractedHeaders
}
