const nlp = require('compromise')
nlp.extend(require('compromise-numbers'))
nlp.extend(require('compromise-dates'))
var thesaurus = require("thesaurus");
const findType = require('./findType')
const createMatrixForAll = require('./createMatrixForAll')

module.exports = (command, attributes, data, featureMatrix, synonymMatrix) => {
    let doc = nlp(command)
    let catchSynonymCommand = nlp(command);
    // const {featureMatrix, synonymMatrix} = createMatrixForAll(attributes, data)
    for(let i = 0; i < attributes.length; i++) {
        if(doc.match(attributes[i])) {
            doc.replace(attributes[i], findType(attributes[i], data))
        }
    }
    for (let i = 0; i < featureMatrix.length; i++) {
        for (let n = 0; n < featureMatrix[i].length; n++) {
            if (doc.match(featureMatrix[i][n])) {
                doc.replace(featureMatrix[i][n], findType(featureMatrix[i][0], data))
            }
        }
    }
    doc.numbers().replaceWith("quantitative")
    doc.dates().replaceWith("temporal")
    for(let i = 0; i < synonymMatrix.length; i++){
        for(let n = 0; n < synonymMatrix[i].length; n++){
            if(catchSynonymCommand.text().includes(synonymMatrix[i][n].toLowerCase())){
                catchSynonymCommand.replace(synonymMatrix[i][n], synonymMatrix[i][0])
            }
        }
    }

    generalizedCommand = doc.text()
    synonymCommand = catchSynonymCommand.text()
    return {generalizedCommand, synonymCommand}
}


