const nlp = require('compromise')
const { NetworkAuthenticationRequire } = require('http-errors')
const lemmatize = require('wink-lemmatizer')

module.exports = (command) => {
    let doc = nlp(command)
    
    // doc.nouns().toSingular()
    return doc.text()
}