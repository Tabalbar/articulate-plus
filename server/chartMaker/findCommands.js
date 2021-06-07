const nlp = require('compromise')
module.exports = (command) => {
    let doc = nlp(command)

    const commands = doc.splitBefore("#Verb").out('array')
    // const commands = doc.verbs().out('array')

    return commands
}