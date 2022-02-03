const nlp = require('compromise')
const findType = require('./findType')

module.exports = (intent, command, headers, data, headerMatrix, actualCommand) => {
    let chartObj = {
        charts: null,
        errMsg: 'testing waters'
    };
    let filteredHeaders = extractFilteredHeaders(command, headerMatrix, data, headers, command)
    let extractedHeaders = extractHeaders(command, headers, filteredHeaders)
    return chartObj
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



function extractHeaders(command, headers, filteredHeaders) {
    let doc = nlp(command)
    let extractedHeaders = []
    for (let i = 0; i < headers.length; i++) {
        if (doc.has(headers[i])) {
            extractedHeaders.push(headers[i])
        }
    }
    let accessors = []
    let keys = Object.keys(filteredHeaders);
    for (let i = 0; i < keys.length; i++) {
        let found = false;
        if (filteredHeaders[keys[i]].length > 0) {
            for (let n = 0; n < extractedHeaders.length; n++) {
                if (extractedHeaders[n] === keys[i]) {
                    found = true
                }
            }
            if (!found) {
                extractedHeaders.push(keys[i])
            }
        }

    }
    return extractedHeaders;
}