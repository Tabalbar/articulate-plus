
const nlp = require('compromise')
const findType = require('./findType')
const findMissing = require('./findMissing').findMissing
const title = require('./specifications/title')
const size = require('./specifications/size')
const mark = require('./specifications/mark')
const encoding = require('./specifications/encoding')
const transform = require('./specifications/transform')
const plotlyPipeline = require('./plotly/plotlyPipeline')
// let chart = chartMaker.chartMaker(explicitChart, synonymCommand, attributes, data, headerMatrix, command, headerFreq, randomChart)
// chartObj.push(chartMaker.chartMaker(response.classifications[i].intent, synonymCommand, attributes, data, headerMatrix, command, headerFreq))

module.exports = {
    chartMaker: function chartMaker(chartMsg) {
        let filteredHeaders = extractFilteredHeaders(command, headerMatrix, data, headers, command)
        let extractedHeaders = extractHeaders(command, headers, data)
        let normalize = checkNormalize(command)

        const headerKeys = Object.keys(headerFreq)
        for (let i = 0; i < headerKeys.length; i++) {
            for (let j = 0; j < headerFreq[headerKeys[i]].length; j++) {
                if (headerFreq[headerKeys[i]][j].count >= 5) {
                    extractedHeaders.push(headerFreq[headerKeys[i]][j].header)
                }
            }
        }
        let charts = []

        let chartObj = {
            plotly: false,
            randomChart: randomChart,
            charts: {
                spec: {
                    title: "",
                    width: 0,
                    height: 0,
                    mark: "",
                    transform: [],
                    concat: [],
                    encoding: {
                        column: {},
                        y: {},
                        x: {},
                        color: {}
                    },
                    data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array

                }
            },
            extraCharts: [],
            errMsg: ''
        };
        let sizeGraph = 'medium'
        if (intent == 'radar') {
            return plotlyPipeline(actualCommand, extractedHeaders, filteredHeaders, data, headerFreq, command)
        }
        chartObj = title(chartObj, actualCommand)
        chartObj = size(chartObj, sizeGraph)
        chartObj, layerMark = mark(chartObj, intent, extractedHeaders)
        chartObj = encoding(chartObj, intent, extractedHeaders, data, headerFreq, command, normalize)
        chartObj = transform(data, filteredHeaders, chartObj)
        charts.push(chartObj)
        return chartObj
    }
}


function extractHeaders(command, headers, data) {

    let doc = nlp(command)
    let extractedHeaders = []

    for (let i = 0; i < headers.length; i++) {
        if (doc.has(headers[i].toLowerCase())) {
            extractedHeaders.push(headers[i])
        }
    }
    let accessors = []
    // let keys = Object.keys(filteredHeaders);
    // for (let i = 0; i < keys.length; i++) {
    //     let found = false;
    //     if (filteredHeaders[keys[i]].length > 0 ) {
    //         for (let n = 0; n < extractedHeaders.length; n++) {
    //             if (extractedHeaders[n] === keys[i]) {
    //                 found = true
    //             }
    //         }
    //         if (!found) {
    //             extractedHeaders.push(keys[i])
    //         }
    //     }

    // }

    if (doc.has("overtime") || doc.has("time")) {
        let foundTime = false
        for (let i = 0; i < extractedHeaders.length; i++) {
            if (findType(extractedHeaders[i], data) === "temporal") {
                foundTime = true
                break
            }
        }
        if (!foundTime) {
            for (let i = 0; i < headers.length; i++) {
                if (findType(headers[i], data) === "temporal") {
                    extractedHeaders.push(headers[i])
                    break;
                }
            }
        }
    }
    return extractedHeaders;
}

function extractFilteredHeaders(command, headerMatrix, data, headers, command) {
    let doc = nlp(command)
    let extractedFilteredHeaders = []
    let foundTimeHeader = false
    for (let i = 0; i < headerMatrix.length; i++) {
        extractedFilteredHeaders[headerMatrix[i][0]] = []
        for (let n = 1; n < headerMatrix[i].length; n++) {
            if (doc.has(headerMatrix[i][n])) {
                extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][n])
            }

        }

        if (findType(headerMatrix[i][0], data) === "temporal" && !foundTimeHeader) {
            const { foundTime, timeHeader } = extractHeadersWithoutFilter(doc, headers, data, command)
            if (!foundTime) {
                findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]])
                command += " " + headerMatrix[i][0]
                foundTimeHeader = true;

            } else {
                if (timeHeader === headerMatrix[i][0]) {
                    findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]])

                }


            }


        }

    }

    function findDates(docCommand, header) {
        if (docCommand.match("to") || docCommand.match("through") || docCommand.match("and")) {
            let termsBefore = docCommand.before('to').terms().out('array')
            let termsAfter = docCommand.after('to').terms().out('array')
            const yearBefore = termsBefore[termsBefore.length - 1]
            const yearAfter = termsAfter[0]
            if (!isNaN(yearBefore) && !isNaN(yearAfter)) {
                header.push(yearBefore)
                header.push(yearAfter)

            }

        }
    }

    function extractHeadersWithoutFilter(docCommand, headers, data) {
        let extractedHeaders = []
        let foundTime = false
        let index;
        for (let i = 0; i < headers.length; i++) {

            if (docCommand.has(headers[i]) && findType(headers[i], data) === "temporal") {
                index = i;
                foundTime = true
                break;
            }
        }
        let timeHeader = headers[index]
        return { foundTime, timeHeader }
    }
    return extractedFilteredHeaders;
}



/* 
Function used to calculate the number of unique words for a category.
This is used to infer what to parse in the comparison branch
 
Args:
    Extracted headers -> keyword attributes extracted from the command
    Data: Actual data from data set
 
Returns: 
    Vector length of unique words from every attribute header
*/
function countCategories(extractedHeeader, data) {
    const unique = [...new Set(data.map(item => item[extractedHeeader]))];
    return unique.length
}
