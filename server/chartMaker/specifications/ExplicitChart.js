const nlp = require("compromise")
const chartOptions = require('./chartOptions')
module.exports = (command) => {
    let doc = nlp(command)
    for (let i = 0; i < chartOptions.length; i++) {

        if (doc.has(chartOptions[i].key)) {

            return chartOptions[i].mark
        }
    }
    return false

}