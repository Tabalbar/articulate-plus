import React, { useState, useEffect } from "react";
import { VegaLite } from "react-vega";
import { Box } from "@chakra-ui/react";

const StreamGraph = ({
  attributes,
  synonymAttributes,
  featureAttributes,
  overHearingData,
}) => {
  const [streamData, setStreamData] = useState([]);
  const [sentecesLength, setSentencesLength] = useState(0);

  const specification = {
    width: 500,
    height: 250,
    mark: "rect",
    encoding: {
      x: {
        field: "sentence",
        type: "ordinal",
      },
      y: {
        type: "nominal",
        field: "header",
      },
      color: {
        aggregate: "count",
        scale: { scheme: "reds" },
        type: "quantitative",
      },
      tooltip: { field: "header", type: "nominal" },
    },
    config: {
      axis: { grid: true, tickBand: "extent" },
    },
    data: { name: "table" },
  };
  useEffect(() => {
    if (streamData.length == 0) {
      let tmpStreamData = [];
      for (let i = 0; i < synonymAttributes.length; i++) {
        tmpStreamData.push({ header: synonymAttributes[i][0], sentence: 0 });
      }
      setStreamData(tmpStreamData.flat());
    }
  }, []);
  console.log(streamData);
  useEffect(() => {
    let sentences = overHearingData.split(".");
    let transcriptLength = sentences.length;
    // if (sentences.length % 5 == 0) {
    let tmpSynonymAttributes = synonymAttributes;
    let synonymsAndFeatures = [];

    for (let i = 0; i < featureAttributes.length; i++) {
      synonymsAndFeatures.push(
        featureAttributes[i].concat(tmpSynonymAttributes[i])
      );
    }
    let tmpStreamData = streamData;
    sentences = sentences.slice(-1);
    let attributesWereFound = false;
    for (let i = 0; i < sentences.length; i++) {
      let words = sentences[i].split(" ");
      for (let m = 0; m < words.length; m++) {
        for (let j = 0; j < synonymsAndFeatures.length; j++) {
          let found = false;
          for (let w = 0; w < synonymsAndFeatures[j].length; w++) {
            if (
              words[m]
                .toLowerCase()
                .includes(synonymsAndFeatures[j][w].toLowerCase())
            ) {
              tmpStreamData.push({
                header: synonymsAndFeatures[j][0],
                sentence: transcriptLength,
              });
              found = true;
              attributesWereFound = true;
              break;
            }
          }
          if (found) break;
        }
      }
    }
    if (tmpStreamData.length > 0) {
      setStreamData(tmpStreamData.flat());
    }
  }, [overHearingData]);
  return (
    <>
      <VegaLite
        width={parseInt(window.innerWidth - 250)}
        spec={specification}
        data={{ table: streamData }}
      />
    </>
  );
};

export default StreamGraph;
