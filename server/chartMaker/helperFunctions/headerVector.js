const nlp = require('compromise')

module.exports = (headers) => {
    let synonyms = []
    let synonymMatrix = [];

    for (let i = 0; i < headers.length; i++) {
        synonyms = [headers[i]]

        if(headers[i].match(/\W/g)){
            let words = headers[i].split(/\W/g)
            for(let i = 0; i < words.length; i++){
                let doc = nlp(words[i])
                if(doc.has('#Noun')){
                    synonyms.push(words[i])
                
                } else if(i == 0) {                    
                    synonyms.push(words[i])
                }
            }

        }
        synonyms = synonyms.flat()

        synonymMatrix.push(synonyms)

    }
    return synonymMatrix

}