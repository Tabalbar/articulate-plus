const findType = require("../createCharts/helperFunctions/findType");
const Sentiment = require("sentiment");

module.exports = (transcript, featureMatrix, data, modifiedChartOptions) => {
  let wordCount = [];

  for (let i = 0; i < featureMatrix.length; i++) {
    wordCount.push({ header: featureMatrix[i][0], filters: [] });
    for (let j = 1; j < featureMatrix[i].length; j++) {
      wordCount[i].filters.push({ filter: featureMatrix[i][j], count: 0 });
    }
  }
  let sentences = transcript.split(".");
  sentences = sentences.slice(-modifiedChartOptions.filter.pastSentences);

  if (
    modifiedChartOptions.sentimentAnalysis &&
    modifiedChartOptions.filter.toggle
  ) {
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < featureMatrix.length; w++) {
          for (let n = 1; n < featureMatrix[w].length; n++) {
            if (words[j].toLowerCase().includes(featureMatrix[w][n])) {
              const sentiment = new Sentiment();
              const result = sentiment.analyze(sentences[i]);
              console.log(featureMatrix[w][n]);
              if (result.score >= 0) {
                wordCount[w].filters[n - 1].count += 1;
              } else {
                wordCount[w].filters[n - 1].count -= 1;
              }
              break;
            }
          }
        }
      }
    }
  } else if (modifiedChartOptions.filter.toggle) {
    sentences.slice(-modifiedChartOptions.filter.pastSentences);
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < featureMatrix.length; w++) {
          let found = false;
          for (let n = 1; n < featureMatrix[w].length; n++) {
            if (words[j].toLowerCase().includes(featureMatrix[w][n])) {
              wordCount[w].filters[n - 1].count += 1;
              found = true;
              break;
            }
          }
          if (found) break;
        }
      }
    }
  }

  return wordCount;
};
