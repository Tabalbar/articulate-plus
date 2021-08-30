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
    mark: { type: "area", interpolate: "step" },
    encoding: {
      x: {
        field: "date",
        axis: null,
      },
      y: {
        aggregate: "count",
        field: "header",
      },
      color: { field: "header" },
    },
    data: { name: "table" },
  };
  //   useEffect(() => {
  //     let tmpStreamData = [];
  //     for (let i = 0; i < attributes.length; i++) {
  //       tmpStreamData.push({ header: attributes[i], count: 0, date: new Date() });
  //     }

  //     setStreamData(tmpStreamData);
  //   }, [attributes]);

  useEffect(() => {
    let sentences = overHearingData.split(".");
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
    for (let i = 0; i < sentences.length; i++) {
      for (let j = 0; j < synonymsAndFeatures.length; j++) {
        for (let w = 0; w < synonymsAndFeatures[j].length; w++) {
          if (
            sentences[i]
              .toLowerCase()
              .includes(synonymsAndFeatures[j][w].toLowerCase())
          ) {
            tmpStreamData.push({
              header: synonymsAndFeatures[j][0],
              date: new Date(),
            });
            break;
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
