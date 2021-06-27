const createVector = require('../createVector')
const nlp = require('compromise')
const mark = require('../helperFunctions/mark')
const encoding = require('./encoding')
const transform = require('../helperFunctions/transform')
const createDate = require('../helperFunctions/createDate')
const title = require('../helperFunctions/title')

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
                height: 270,
                mark: "",
                transform: [],
                concat: [],
                encoding: {
                    column: {},
                    y: {},
                    x: {},
                    axis: {
                        format: "%Y",
                        labelAngle: 45
                    }
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
    chartObj = mark(chartObj, intent)
    chartObj = encoding(chartObj, intent, extractedHeaders, chartMsg.data)
    chartObj = transform(chartMsg.data, filteredHeaders, chartObj)
    chartObj.charts.spec.title = title(extractedHeaders, intent)
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