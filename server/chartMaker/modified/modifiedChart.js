
const nlp = require('compromise')
const createVector = require('../createVector')
const countVector = require('./countVector')
const transform = require('../helperFunctions/transform')
const mark = require('../helperFunctions/mark')
const findType = require('../helperFunctions/findType')
const encoding = require('../inferred/encoding')
const createDate = require('../helperFunctions/createDate')
const title = require('../helperFunctions/title')


// let chart = chartMaker.chartMaker(explicitChart, synonymCommand, attributes, data, headerMatrix, command, headerFreq, randomChart)
// chartObj.push(chartMaker.chartMaker(response.classifications[i].intent, synonymCommand, attributes, data, headerMatrix, command, headerFreq))

module.exports = (intent, chartMsg, modifiedChartOptions) => {
    const headerMatrix = createVector(chartMsg.attributes, chartMsg.data)
    let filteredHeaders = extractFilteredHeaders(chartMsg.synonymCommand, headerMatrix, chartMsg.data, chartMsg.attributes, chartMsg.command)
    let extractedHeaders = extractHeaders(chartMsg.synonymCommand, chartMsg.attributes, chartMsg.data, intent)

    if(extractedHeaders.length == 0) {
        return ""
    }
    const { headerFreq } = countVector(chartMsg.transcript, chartMsg.featureMatrix, chartMsg.synonymMatrix, chartMsg.data, modifiedChartOptions)
    const headerKeys = Object.keys(headerFreq)
    for (let i = 0; i < headerKeys.length; i++) {
        for (let j = 0; j < headerFreq[headerKeys[i]].length; j++) {
            if (headerFreq[headerKeys[i]][j].count >= 5) {
                let found = false
                for (let n = 0; n < extractedHeaders.length; n++) {
                    if (extractedHeaders[n] == headerFreq[headerKeys[i]][j].header) {
                        found = true
                    }
                }
                if (!found) {
                    extractedHeaders.push(headerFreq[headerKeys[i]][j].header)
                }
            }
        }
    }

    let chartObj = {
        charts: {
            spec: {
                title: "",
                width: {step: 15},
                mark: "",
                transform: [],
                concat: [],
                encoding: {
                    column: {},
                    y: {},
                    x: {}
                },
                initialized: createDate(),
                timeChosen: '',
                timeClosed: '',
                timeSpentHovered: 0,
                data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array
                command: chartMsg.command
            },

        }
    };
    // chartObj = title(chartObj, actualCommand)
    chartObj = mark(chartObj, intent)
    chartObj = encoding(chartObj, intent, extractedHeaders, chartMsg.data, headerFreq, chartMsg.command)
    chartObj = transform(chartMsg.data, filteredHeaders, chartObj, intent)
    chartObj.charts.spec.title = title(extractedHeaders, intent, filteredHeaders)

    return chartObj
}



function extractHeaders(command, headers, data, intent) {

    let doc = nlp(command)
    let extractedHeaders = []
    for (let i = 0; i < headers.length; i++) {
        if (doc.has(headers[i].toLowerCase())) {
            extractedHeaders.push(headers[i])
        }
    }
    let accessors = []

    if(intent === "map") {
        let mapFound = false;
        for(let i = 0; i < extractedHeaders.length; i ++) {
            if(extractedHeaders[i] == "map") {
                mapFound = true;
            }
        }
        if(!mapFound) {
            for(let i = 0; i < headers.length; i++) {
                if(headers[i] == "map") {
                    extractedHeaders.push(headers[i])
                }
            }
        }

    }
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
    doc.nouns().toSingular()
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
