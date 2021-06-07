const nlp = require('compromise')
const { NetworkAuthenticationRequire } = require('http-errors')
const lemmatize = require('wink-lemmatizer')

module.exports = (command) => {
    let doc = nlp(command)
    
    // let newCommand = doc.nouns().toSingular()
    // console.log(newCommand.text())
    return doc.text()
}