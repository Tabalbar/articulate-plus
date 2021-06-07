const nlp = require("compromise")
const findType = require('./findType')

module.exports = {
    findMissing: function (extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence) {
        if(extractedHeaders.length == 0) {
            return ""
        }
        let missing = reorder(extractedHeaders, targetHeaderLength, data, sequence)
        if (missing.n) {
            extractedHeaders = findInferHeader(command, headerFreq, 'nominal', extractedHeaders)
            return module.exports.findMissing(extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence)
        }
        if (missing.q) {
            extractedHeaders = findInferHeader(command, headerFreq, 'quantitative', extractedHeaders)
            return module.exports.findMissing(extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence)
        }
        if (missing.t) {
            extractedHeaders = findInferHeader(command, headerFreq, 'temporal', extractedHeaders)
            return module.exports.findMissing(extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence)
        }
        if (missing.q2) {
            extractedHeaders = findInferHeader(command, headerFreq, 'quantitative', extractedHeaders)
            return module.exports.findMissing(extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence)
        }
        if (missing.q3) {
            extractedHeaders = findInferHeader(command, headerFreq, 'quantitative', extractedHeaders)
            return module.exports.findMissing(extractedHeaders, data, targetHeaderLength, headerFreq, command, sequence)
        }
        return extractedHeaders
    }
}


function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
    let tmpHeader = extractedHeaders[targetIndex]
    extractedHeaders[targetIndex] = extractedHeaders[sourceIndex]
    extractedHeaders[sourceIndex] = tmpHeader
    return extractedHeaders
}



function findInferHeader(command, headerFreq, type, extractedHeaders) {

    let headerIndex = 0;
    if (headerFreq[type].length == 0) {
        return ""
    }
    let headerToAdd = headerFreq[type][headerIndex].header

    for (let i = 1; i < headerFreq[type].length; i++) {
        if (headerFreq[type][headerIndex].count < headerFreq[type][i].count) {
            headerToAdd = headerFreq[type][i].header
            headerIndex = i
        }
    }

    for (let i = 0; i < extractedHeaders.length; i++) {
        if (extractedHeaders[i] == headerFreq[type][headerIndex].header) {
            headerFreq[type].splice(headerIndex, 1)
            return findInferHeader(command, headerFreq, type, extractedHeaders)
        }
    }
    extractedHeaders.push(headerToAdd)


    command += " " + headerToAdd
    return extractedHeaders
}

function reorder(extractedHeaders, targetHeaderLength, data, sequence) {
    let missing = {
        n: true,
        q: true,
        t: true,
        q2: true,
        q3: true
    }
    switch (sequence) {
        case "NQT":
            missing = {
                n: true,
                q: true,
                t: true,
                q2: false,
                q3: false
            }
            //For length 1
            if (targetHeaderLength == 1) {
                missing.t = false
                missing.q = false
                if (extractedHeaders.length > 0 && findType(extractedHeaders[0], data) == 'nominal') {
                    missing.n = false
                    break;
                }
            }

            //For length 2
            if (targetHeaderLength == 2) {
                missing.t = false
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'nominal') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.n = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q = false
                        break
                    }
                }
            }

            //for length 3
            if (targetHeaderLength == 3) {
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'nominal') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.n = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q = false
                        break
                    }
                }
                for (let i = 2; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'temporal') {
                        extractedHeaders = switchHeaders(extractedHeaders, 2, i)
                        missing.t = false
                        break
                    }
                }
            }
            return missing
            break;
        case "QQQ":
            missing = {
                n: false,
                q: true,
                t: false,
                q2: true,
                q3: true
            }
            //For length 2
            if (targetHeaderLength == 2) {
                missing.q3 = false
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.q = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q2 = false
                        break
                    }
                }
            }

            //for length 3
            if (targetHeaderLength == 3) {
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.q = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q2 = false
                        break
                    }
                }
                for (let i = 2; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 2, i)
                        missing.q3 = false
                        break
                    }
                }
            }
            return missing
        case "NQN":
            missing = {
                n: true,
                q: true,
                t: false,
                q2: false,
                q3: false,
            }

            //For length 1
            if (targetHeaderLength == 1) {
                missing.q = false
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'nominal') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.n = false
                        break
                    }
                }
            }

            //For length 2
            if (targetHeaderLength == 2) {
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'nominal') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.n = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q = false
                        break
                    }
                }
            }

            //for length 3
            if (targetHeaderLength >= 3) {
                for (let i = 0; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 0, i)
                        missing.n = false
                        break
                    }
                }
                for (let i = 1; i < extractedHeaders.length; i++) {
                    if (findType(extractedHeaders[i], data) == 'quantitative') {
                        extractedHeaders = switchHeaders(extractedHeaders, 1, i)
                        missing.q = false
                        break
                    }
                }
            }
            return missing
        default:
            break;
    }
}