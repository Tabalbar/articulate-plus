import React, { useState, useEffect } from "react";
import ReactWordCloud from "react-wordcloud";

function WordCloud({
  overHearingData,
  attributes,
  synonymAttributes,
  featureAttributes,
}) {
  const [words, setWords] = useState([]);

  useEffect(() => {
    let tmpWords = [];
    for (let i = 0; i < attributes.length; i++) {
      tmpWords.push({ text: attributes[i], value: 0 });
    }
    setWords(tmpWords);
  }, [attributes]);
  useEffect(() => {
    if (words.length > 0) {
      let tmpSynonymAttributes = synonymAttributes;
      let synonymsAndFeatures = [];

      for (let i = 0; i < featureAttributes.length; i++) {
        synonymsAndFeatures.push(
          featureAttributes[i].concat(tmpSynonymAttributes[i])
        );
      }
      let sentences = overHearingData.split(".");
      let lastSentence = sentences.slice(-1)[0];
      let tmpWords = words;
      for (let i = 0; i < featureAttributes.length; i++) {
        for (let j = 0; j < featureAttributes[i].length; j++) {
          if (
            lastSentence
              .toLowerCase()
              .includes(featureAttributes[i][j].toLowerCase())
          ) {
            tmpWords[i].value += 1;
            break;
          }
        }
      }
      setWords(tmpWords);
      // if (sentences.length > setnencesLength) {
      //   let lastSentence = sentences[sentences.length - 1];
      //   for (let i = 0; i < synonymAttributes.length; i++) {
      //     for (let j = 0; j < synonymAttributes[i].length; j++) {
      //       if (
      //         lastSentence
      //           .toLowerCase()
      //           .includes(synonymAttributes[i][j].toLowerCase())
      //       ) {
      //         tmpWords[i].value += 1;
      //       }
      //     }
      //   }
      //   for (let i = 0; i < featureAttributes.length; i++) {
      //     for (let j = 0; j < featureAttributes[i].length; j++) {
      //       if (
      //         lastSentence
      //           .toLowerCase()
      //           .includes(featureAttributes[i][j].toLowerCase())
      //       ) {
      //         tmpWords[i].value += 1;
      //       }
      //     }
      //   }
      // }
      setWords(tmpWords);
    }
  }, [overHearingData]);

  const options = {
    enableTooltip: true,
    deterministic: true,
    rotations: 0,
    fontSizes: [10, 30],
  };
  return (
    <>
      <div style={{ height: "30vh", width: "100vw" }}>
        <ReactWordCloud words={words} options={options} />
      </div>
    </>
  );
}

export default WordCloud;
