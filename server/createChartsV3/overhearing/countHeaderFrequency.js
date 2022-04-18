const findType = require("../charts/helpers/findType");
const Sentiment = require("sentiment");

module.exports = (chartMsg, options) => {
  let tmpSynonymAttributes = chartMsg.synonymMatrix;
  let synonymsAndFeatures = [];
  let headerFrequencyCount = {
    nominal: [],
    quantitative: [],
    temporal: [],
    map: [],
    sentences: [],
  };
  for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
    synonymsAndFeatures.push(
      chartMsg.featureMatrix[i].concat(tmpSynonymAttributes[i])
    );
  }

  let wordCount = [];
  for (let i = 0; i < synonymsAndFeatures.length; i++) {
    wordCount.push({ header: synonymsAndFeatures[i][0], count: 0 });
  }

  let sentences = chartMsg.transcript.split(".");
  if (options.window.pastSentences === 0) {
    sentences = [];
  } else {
    sentences = sentences.slice(-options.window.pastSentences);
  }
  headerFrequencyCount.sentences = sentences;
  // if (options.sentimentAnalysis && options.window.toggle) {
  //   for (let i = 0; i < sentences.length; i++) {
  //     let words = sentences[i].split(" ");
  //     for (let j = 0; j < words.length; j++) {
  //       for (let w = 0; w < synonymsAndFeatures.length; w++) {
  //         for (let n = 0; n < synonymsAndFeatures[w].length; n++) {
  //           if (words[j].toLowerCase().includes(synonymsAndFeatures[w][n])) {
  //             const sentiment = new Sentiment();
  //             const result = sentiment.analyze(sentences[i]);
  //             if (result.score >= 0) {
  //               wordCount[w].count += 1;
  //             } else {
  //               wordCount[w].count -= 1;
  //             }
  //             break;
  //           }
  //         }
  //       }
  //     }
  //   }
  //   for (let i = 0; i < wordCount.length; i++) {
  //     headerFrequencyCount[findType(wordCount[i].header, chartMsg.data)].push(
  //       wordCount[i]
  //     );
  //   }
  //   return headerFrequencyCount;
  // } else
  if (options.window.toggle) {
    // sentences.slice(-options.window.pastSentences);
    for (let i = 0; i < sentences.length; i++) {
      // const result = message.replace(/JS/g, "JavaScript");
      for (let j = 0; j < synonymsAndFeatures.length; j++) {
        for (let k = 0; k < synonymsAndFeatures[j].length; k++) {
          if (sentences[i].toLowerCase().includes(synonymsAndFeatures[j][k])) {
            wordCount[j].count += 1;
            break;
          }
        }
      }
    }
    // for (let i = 0; i < sentences.length; i++) {
    //   let words = sentences[i].split(" ");
    //   for (let j = 0; j < words.length; j++) {
    //     for (let w = 0; w < synonymsAndFeatures.length; w++) {
    //       let found = false;
    //       for (let n = 0; n < synonymsAndFeatures[w].length; n++) {
    //         if (words[j].toLowerCase().includes(synonymsAndFeatures[w][n])) {
    //           wordCount[w].count += 1;
    //           found = true;
    //           break;
    //         }
    //       }
    //       if (found) break;
    //     }
    //   }
    // }
    for (let i = 0; i < wordCount.length; i++) {
      headerFrequencyCount[findType(wordCount[i].header, chartMsg.data)].push(
        wordCount[i]
      );
    }
    return headerFrequencyCount;
  } else {
    for (let i = 0; i < wordCount.length; i++) {
      headerFrequencyCount[findType(wordCount[i].header, chartMsg.data)].push(
        wordCount[i]
      );
    }

    return headerFrequencyCount;
  }
};
