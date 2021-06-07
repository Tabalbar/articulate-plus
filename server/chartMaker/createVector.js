const nlp = require('compromise')
const findType = require('./findType')

module.exports = (headers, data) => {
    let featureMatrix = [];
    for (let i = 0; i < headers.length; i++) {
        if (findType(headers[i], data) === "nominal") {
            var flags = [], output = [headers[i]], l = data.length, n;
            for (n = 0; n < l; n++) {
                if (flags[data[n][headers[i]]]) continue;
                flags[data[n][headers[i]]] = true;
                output.push(data[n][headers[i]]);
            }
            featureMatrix.push(output)
        } else {
            featureMatrix.push([headers[i]])
        }
    }
    return featureMatrix
}
