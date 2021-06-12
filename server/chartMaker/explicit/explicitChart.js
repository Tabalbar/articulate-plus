const createVector = require('../createVector')
const nlp = require('compromise')
const mark = require('../helperFunctions/mark')
const encoding = require('./encoding')
const transform = require('./transform')

// let chart = chartMaker.chartMaker(explicitChart, synonymCommand, attributes, data, headerMatrix, command, headerFreq, randomChart)

module.exports = (intent, chartMsg) => {
    let extractedHeaders = extractHeaders(chartMsg.synonymCommand, chartMsg.attributes)
    const headerMatrix = createVector(chartMsg.attributes, chartMsg.data)
    let filteredHeaders = extractFilteredHeaders(chartMsg.command, headerMatrix)
    let chartObj = {
        charts: {
            spec: {
                title: "",
                width: 400,
                height: 300,
                mark: "",
                transform: [],
                concat: [],
                encoding: {
                    y: {},
                    x: {},
                },
                data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array

            }
        }
    };
    chartObj = mark(chartObj, intent)
    chartObj = encoding(chartObj, intent, extractedHeaders, chartMsg.data)
    chartObj = transform(chartMsg.data, filteredHeaders, chartObj)
    console.log(chartObj.charts.spec)
    return chartObj
}

function extractHeaders(command, headers) {
    let doc = nlp(command)
    let extractedHeaders = []
    for (let i = 0; i < headers.length; i++) {
        if (doc.has(headers[i].toLowerCase())) {
            extractedHeaders.push(headers[i])
        }
    }
    let accessors = []
    return extractedHeaders;
}

function extractFilteredHeaders(command, headerMatrix) {
    let doc = nlp(command)
    let extractedFilteredHeaders = []
    for(let i = 0; i < headerMatrix.length; i++) {
        extractedFilteredHeaders[headerMatrix[i][0]] = []
        for(let j = 1; j < headerMatrix[i].length; j++) {
            if (doc.has(headerMatrix[i][j])) {
                extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][j])
            }        
        }
    }
    return extractedFilteredHeaders
}

// function extractFilteredHeaders(command, headerMatrix, data, headers, command) {
//     let doc = nlp(command)
//     let extractedFilteredHeaders = []
//     let foundTimeHeader = false
//     for (let i = 0; i < headerMatrix.length; i++) {
//         extractedFilteredHeaders[headerMatrix[i][0]] = []
//         for (let n = 1; n < headerMatrix[i].length; n++) {
//             if (doc.has(headerMatrix[i][n])) {
//                 extractedFilteredHeaders[headerMatrix[i][0]].push(headerMatrix[i][n])
//             }

//         }

//         if (findType(headerMatrix[i][0], data) === "temporal" && !foundTimeHeader) {
//             const { foundTime, timeHeader } = extractHeadersWithoutFilter(doc, headers, data, command)
//             if (!foundTime) {
//                 findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]])
//                 command += " " + headerMatrix[i][0]
//                 foundTimeHeader = true;

//             } else {
//                 if (timeHeader === headerMatrix[i][0]) {
//                     findDates(doc, extractedFilteredHeaders[headerMatrix[i][0]])

//                 }


//             }


//         }

//     }

//     function findDates(docCommand, header) {
//         if (docCommand.match("to") || docCommand.match("through") || docCommand.match("and")) {
//             let termsBefore = docCommand.before('to').terms().out('array')
//             let termsAfter = docCommand.after('to').terms().out('array')
//             const yearBefore = termsBefore[termsBefore.length - 1]
//             const yearAfter = termsAfter[0]
//             if (!isNaN(yearBefore) && !isNaN(yearAfter)) {
//                 header.push(yearBefore)
//                 header.push(yearAfter)

//             }

//         }
//     }

//     function extractHeadersWithoutFilter(docCommand, headers, data) {
//         let extractedHeaders = []
//         let foundTime = false
//         let index;
//         for (let i = 0; i < headers.length; i++) {

//             if (docCommand.has(headers[i]) && findType(headers[i], data) === "temporal") {
//                 index = i;
//                 foundTime = true
//                 break;
//             }
//         }
//         let timeHeader = headers[index]
//         return { foundTime, timeHeader }
//     }
//     return extractedFilteredHeaders;
// }

