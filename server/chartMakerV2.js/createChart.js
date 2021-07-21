const headers = require('./headers')
const findUniqueNominalData = require('./findUniqueNominalData')
const frequencyCounterOverhearing = require('./frequencyCounterOverhearing')

module.exports = (chartMsg, intent, options) => {
    const uniqueNominalData = findUniqueNominalData(chartMsg.attributes, chartMsg.data)
    let extractedHeaders = headers.extractHeaders(chartMsg.synonymCommand, chartMsg.attributes, chartMsg.data, intent)
    let extractedHeaders = headers.extractFilteredData(chartMsg.synonymCommand, uniqueNominalData, chartMsg.data, chartMsg.attributes, chartMsg.command)
    
    //todo if options.overhearingOn then do this
    const { headerFreq } = frequencyCounterOverhearing(chartMsg.transcript, chartMsg.featureMatrix, chartMsg.synonymMatrix, chartMsg.data, options)
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
                width: 400,
                height: 220,
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
}
