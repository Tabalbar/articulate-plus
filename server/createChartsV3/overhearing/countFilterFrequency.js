const Sentiment = require("sentiment");

module.exports = (chartMsg, options) => {
  let wordCount = [];

  for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    wordCount.push({ header: chartMsg.featureMatrix[i][0], filters: [] });
    for (let j = 1; j < chartMsg.featureMatrix[i].length; j++) {
      wordCount[i].filters.push({
        filter: chartMsg.featureMatrix[i][j],
        count: 0,
      });
    }
  }
  let sentences = chartMsg.transcript.split(".");
  sentences = sentences.slice(-options.filter.pastSentences);

  if (options.sentimentAnalysis && options.filter.toggle) {
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < chartMsg.featureMatrix.length; w++) {
          for (let n = 1; n < chartMsg.featureMatrix[w].length; n++) {
            if (words[j].toLowerCase().includes(chartMsg.featureMatrix[w][n])) {
              const sentiment = new Sentiment();
              const result = sentiment.analyze(sentences[i]);
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
  } else if (options.filter.toggle) {
    sentences.slice(-options.filter.pastSentences);
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let j = 0; j < words.length; j++) {
        for (let w = 0; w < chartMsg.featureMatrix.length; w++) {
          let found = false;
          for (let n = 1; n < chartMsg.featureMatrix[w].length; n++) {
            if (words[j].toLowerCase().includes(chartMsg.featureMatrix[w][n])) {
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
