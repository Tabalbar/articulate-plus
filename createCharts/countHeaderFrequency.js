const nlp = require("compromise");
const findType = require("../server/createChartsV3/charts/helperFunctions/findType");
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
  sentences = sentences.slice(-modifiedChartOptions.window.pastSentences);

  if (
    modifiedChartOptions.sentimentAnalysis &&
    modifiedChartOptions.window.toggle
  ) {
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < synonymsAndFeatures.length; w++) {
          for (let n = 0; n < synonymsAndFeatures[w].length; n++) {
            if (words[j].toLowerCase().includes(synonymsAndFeatures[w][n])) {
              const sentiment = new Sentiment();
              const result = sentiment.analyze(sentences[i]);
              if (result.score >= 0) {
                wordCount[w].count += 1;
              } else {
                wordCount[w].count -= 1;
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
    sentences.slice(-modifiedChartOptions.window.pastSentences);

    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < synonymsAndFeatures.length; w++) {
          let found = false;
          for (let n = 0; n < synonymsAndFeatures[w].length; n++) {
            if (words[j].toLowerCase().includes(synonymsAndFeatures[w][n])) {
              wordCount[w].count += 1;
              found = true;
              break;
            }
          }
          if (found) break;
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
