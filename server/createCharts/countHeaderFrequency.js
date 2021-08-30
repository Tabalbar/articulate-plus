const nlp = require("compromise");
const findType = require("../createCharts/helperFunctions/findType");
const Sentiment = require("sentiment");

module.exports = (
  transcript,
  headerMatrix,
  synonymAttributes,
  data,
  modifiedChartOptions
) => {
  let tmpSynonymAttributes = synonymAttributes;
  let synonymsAndFeatures = [];
  let headerFrequencyCount = {
    nominal: [],
    quantitative: [],
    temporal: [],
    map: [],
  };
  for (let i = 0; i < headerMatrix.length; i++) {
    synonymsAndFeatures.push(headerMatrix[i].concat(tmpSynonymAttributes[i]));
  }

  let wordCount = [];

  for (let i = 0; i < synonymsAndFeatures.length; i++) {
    wordCount.push({ header: synonymsAndFeatures[i][0], count: 0 });
  }

  let sentences = transcript.split(".");
  sentences = sentences.slice(-20);
  if (
    modifiedChartOptions.semanticAnalysis &&
    modifiedChartOptions.window.toggle
  ) {
    for (let i = 0; i < sentences.length; i++) {
      let sentence = nlp(sentences[i]);
      sentence.nouns().toSingular();

      const nouns = sentence.nouns().out("array");
      for (let w = 0; w < nouns.length; w++) {
        for (let j = 0; j < synonymsAndFeatures.length; j++) {
          for (let n = 0; n < synonymsAndFeatures[j].length; n++) {
            if (synonymsAndFeatures[j][n].includes(nouns[w])) {
              const sentiment = new Sentiment();
              const result = sentiment.analyze(sentences[i]);
              if (result.score >= 0) {
                wordCount[j].count += 1;
              } else {
                wordCount[j].count -= 1;
              }
              break;
            }
          }
        }
      }
    }
    for (let i = 0; i < wordCount.length; i++) {
      headerFrequencyCount[findType(wordCount[i].header, data)].push(
        wordCount[i]
      );
    }
    return headerFrequencyCount;
  } else if (modifiedChartOptions.window.toggle) {
    sentences.slice(
      Math.max(sentences.length - modifiedChartOptions.window.pastSenteces, 0)
    );
    for (let i = 0; i < sentences.length; i++) {
      let sentence = nlp(sentences[i]);
      sentence.nouns().toSingular();

      const nouns = sentence.nouns().out("array");

      for (let w = 0; w < nouns.length; w++) {
        for (let j = 0; j < synonymsAndFeatures.length; j++) {
          for (let n = 0; n < synonymsAndFeatures[j].length; n++) {
            if (synonymsAndFeatures[j][n].includes(nouns[w])) {
              console.log(synonymsAndFeatures[j][n], nouns[w]);

              wordCount[j].count += 1;
              break;
            }
          }
        }
      }
    }

    for (let i = 0; i < wordCount.length; i++) {
      headerFrequencyCount[findType(wordCount[i].header, data)].push(
        wordCount[i]
      );
    }
    return headerFrequencyCount;
  } else {
    for (let i = 0; i < wordCount.length; i++) {
      headerFrequencyCount[findType(wordCount[i].header, data)].push(
        wordCount[i]
      );
    }
    return headerFrequencyCount;
  }
};
