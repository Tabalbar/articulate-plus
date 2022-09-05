/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
import React, { useState, useEffect } from "react";
import { VegaLite } from "react-vega";

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
    mark: "area",
    encoding: {
      x: {
        field: "date",
        // axis: null,
      },
      y: {
        aggregate: "sum",
        field: "count",
        stack: "center",
      },
      color: { field: "header" },
    },
    data: { name: "table" },
  };
  useEffect(() => {
    let tmpStreamData = [];
    for (let i = 0; i < attributes.length; i++) {
      tmpStreamData.push({ header: attributes[i], count: 0, date: new Date() });
    }

    setStreamData(tmpStreamData);
  }, [attributes]);

  useEffect(() => {
    let sentences = overHearingData.split(".");
    setSentencesLength(sentences.length);
    let tmpStreamData = streamData;
    if (sentences.length > sentecesLength) {
      let lastSentence = sentences[sentences.length - 1];
      for (let i = 0; i < synonymAttributes.length; i++) {
        for (let j = 0; j < synonymAttributes[i].length; j++) {
          if (
            lastSentence
              .toLowerCase()
              .includes(synonymAttributes[i][j].toLowerCase())
          ) {
            tmpStreamData.push({
              header: synonymAttributes[i][0],
              count: 1,
              date: new Date(),
            });
          }
        }
      }
      for (let i = 0; i < featureAttributes.length; i++) {
        for (let j = 0; j < featureAttributes[i].length; j++) {
          if (
            lastSentence
              .toLowerCase()
              .includes(featureAttributes[i][j].toLowerCase())
          ) {
            tmpStreamData.push({
              header: featureAttributes[i][0],
              count: 1,
              date: new Date(),
            });
          }
        }
      }
    }

    setStreamData(tmpStreamData.flat());
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
