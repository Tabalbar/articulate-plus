const nlp = require("compromise");
const createVector = require("./createVector");
nlp.extend(require("compromise-numbers"));
nlp.extend(require("compromise-dates"));
var thesaurus = require("thesaurus");
const findType = require("../createCharts/helperFunctions/findType");

module.exports = (headers, data) => {
  let featureMatrix = [];
  let synonymMatrix = [];
  for (let i = 0; i < headers.length; i++) {
    synonyms = [headers[i]];
    if (findType(headers[i], data) === "nominal") {
      var flags = [],
        output = [headers[i]],
        l = data.length,
        n;
      for (n = 0; n < l; n++) {
        if (flags[data[n][headers[i]]]) continue;
        flags[data[n][headers[i]]] = true;
        output.push(data[n][headers[i]]);
        // output.push(thesaurus.find(data[n][headers[i]]))
        output = output.flat();
      }
      featureMatrix.push(output);
    } else if (findType(headers[i], data) === "quantitative") {
      var output = [];
      output.push(headers[i]);
      let quantitativeData = [];
      for (let j = 0; j < data.length; j++) {
        let num = parseFloat(data[j][headers[i]]);
        if (isNaN(num)) {
          console.log(num);
        } else {
          quantitativeData.push(num);
        }
      }

      output.push(
        Math.min(...quantitativeData).toString() +
          " - " +
          Math.max(...quantitativeData).toString()
      );
      output = output.flat();

      featureMatrix.push(output);
    } else {
      var output = [headers[i]];
      featureMatrix.push(output);
    }

    if (headers[i].match(/\W/g)) {
      let words = headers[i].split(/\W/g);
      for (let i = 0; i < words.length; i++) {
        let doc = nlp(words[i]);
        if (doc.has("#Noun")) {
          let synonymWords = thesaurus.find(words[i]);
          for (let j = 0; j < synonymWords.length; j++) {
            if (synonymWords[j] === "make") {
              synonymWords.splice(j, 1);
            }
          }
          synonyms.push(synonymWords);
        } else if (i == 0) {
          synonyms.push(words[i]);
          synonyms.push(thesaurus.find(words[i]));
        }
      }
    }
    synonyms.push(thesaurus.find(headers[i].toLowerCase()));
    synonyms = synonyms.flat();

    synonymMatrix.push(synonyms);
  }

  for (let i = 0; i < synonymMatrix.length; i++) {
    for (let j = 1; j < synonymMatrix[i].length; j++) {
      for (let n = 0; n < headers.length; n++) {
        if (synonymMatrix[i][j] === headers[n].toLowerCase()) {
          synonymMatrix[i].splice(j, 1);
        }
      }
    }
  }
  for (let i = 0; i < synonymMatrix.length; i++) {
    if (synonymMatrix[i].length > 18) {
      synonymMatrix[i] = synonymMatrix[i].splice(0, 19);
    }
  }
  return { featureMatrix, synonymMatrix };
};
