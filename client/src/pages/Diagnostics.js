import React, { useEffect, useState } from "react";

//Chakra
import {
  Grid,
  Textarea,
  Box,
  Table,
  Tr,
  Td,
  Th,
  Center,
  Button,
  HStack,
  Text,
} from "@chakra-ui/react";

//Components
import StreamGraph from "../components/diagnostics/StreamGraph";
import WordCloud from "../components/diagnostics/WordCloud";
import LineTheme from "../components/diagnostics/LineTheme";

/**
 * Diagnostics page for Researcher to analyze data
 *
 * @param {object} chartMsg State to send to server
 * @returns
 */
function Diagnostics({ chartMsg, charts }) {
  const [transcriptData, setTranscriptData] = useState([]);
  useEffect(() => {
    localStorage.getItem(chartMsg);
  }, [chartMsg]);

  //Download user's data, charts made, looged transcripts,an
  const downloadFile = async () => {
    let myData = {
      count: makeCount(charts, chartMsg),
      chosenCharts: charts,
      transcript: chartMsg.transcript,
      loggedTranscript: chartMsg.loggedTranscript,
      uncontrolledTranscript: chartMsg.uncontrolledTranscript,
      loggedUncontrolledTranscript: chartMsg.loggedUncontrolledTranscript,
      charts: chartMsg.charts,
      synonymsAndFeatures: chartMsg.synonymMatrix,
    };
    const fileName = "file";
    const json = JSON.stringify(myData);
    const blob = new Blob([json], { type: "application/json" });
    const href = await URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = fileName + ".json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  useEffect(() => {
    let tmpTranscriptData = [];
    let tmpTranscript = chartMsg.transcript;
    let tmpSynonymAttributes = chartMsg.synonymMatrix;
    let synonymsAndFeatures = [];

    for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
      synonymsAndFeatures.push(
        chartMsg.featureMatrix[i].concat(tmpSynonymAttributes[i])
      );
    }

    let words = tmpTranscript.split(" ");
    for (let i = 0; i < words.length; i++) {
      let found = false;
      for (let j = 0; j < synonymsAndFeatures.length; j++) {
        for (let w = 0; w < synonymsAndFeatures[j].length; w++) {
          if (words[i].toLowerCase().includes(synonymsAndFeatures[j][w])) {
            tmpTranscriptData.push({
              word: words[i],
              bold: true,
              header: synonymsAndFeatures[j][0],
            });
            found = true;
            break;
          }
        }
        if (found) break;
      }
      if (!found) {
        tmpTranscriptData.push({ word: words[i], bold: false });
      }
    }
    setTranscriptData(tmpTranscriptData);
  }, [chartMsg.transcript]);
  return (
    <>
      <Center>
        <Button onClick={downloadFile}>Save</Button>
      </Center>
      <Center>
        <Box>
          <div>
            {chartMsg.attributes.length ? (
              <LineTheme
                overHearingData={chartMsg.transcript}
                attributes={chartMsg.attributes}
                chartMsg={chartMsg}
                synonymAttributes={chartMsg.synonymMatrix}
                featureAttributes={chartMsg.featureMatrix}
              />
            ) : null}
          </div>
        </Box>
      </Center>
      <Center>
        <Box>
          <div>
            <WordCloud
              overHearingData={chartMsg.transcript}
              attributes={chartMsg.attributes}
              chartMsg={chartMsg}
              synonymAttributes={chartMsg.synonymMatrix}
              featureAttributes={chartMsg.featureMatrix}
            />
          </div>
        </Box>
      </Center>
      <Center>
        <HStack>
          <Box>
            <Box
              width="40vw"
              height="40vh"
              border="2px"
              p={2}
              overflow="auto"
              borderColor="blackAlpha.200"
              rounded="md"
            >
              <p>
                {transcriptData.map((value, index) => {
                  if (value.bold) {
                    return (
                      <strong>
                        {value.word} ({value.header})
                      </strong>
                    );
                  } else {
                    return value.word + " ";
                  }
                })}
              </p>
            </Box>
          </Box>
          <Box>
            <div>
              <HStack>
                <Table>
                  <Text fontWeight="bold">Total</Text>

                  <Tr>
                    <Th>Attribute</Th>
                    <Th>Frequency Count</Th>
                  </Tr>
                  {chartMsg.total.map.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.total.nominal.map((value, index) => {
                    return (
                      <>
                        <Tr key={index}>
                          <Td> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.total.quantitative.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                </Table>
                <Table>
                  <Text fontWeight="bold">Main AI</Text>

                  <Tr>
                    <Th>Attribute</Th>
                    <Th>Frequency Count</Th>
                  </Tr>
                  {chartMsg.mainAICount.map.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.mainAICount.nominal.map((value, index) => {
                    return (
                      <>
                        <Tr key={index}>
                          <Td> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.mainAICount.quantitative.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                </Table>
                <Table>
                  <Text fontWeight="bold">Main AI With Overhearing</Text>

                  <Tr>
                    <Th>Attribute</Th>
                    <Th>Frequency Count</Th>
                  </Tr>
                  {chartMsg.mainAIOverhearingCount.map.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.mainAIOverhearingCount.nominal.map(
                    (value, index) => {
                      return (
                        <>
                          <Tr key={index}>
                            <Td> {value.header}</Td>
                            <Td> {value.count}</Td>
                          </Tr>
                        </>
                      );
                    }
                  )}
                  {chartMsg.mainAIOverhearingCount.quantitative.map(
                    (value, index) => {
                      return (
                        <>
                          <Tr>
                            <Td key={index}> {value.header}</Td>
                            <Td> {value.count}</Td>
                          </Tr>
                        </>
                      );
                    }
                  )}
                </Table>
              </HStack>
            </div>
          </Box>
        </HStack>
      </Center>
    </>
  );
}

export default Diagnostics;

function makeCount(charts, chartMsg) {
  let chosenCharts = {
    explicit: { count: 0, id: [] },
    mainAI: { count: 0, id: [] },
    mainAIOverhearing: { count: 0, id: [] },
    pivot: { count: 0, id: [] },
    random: { count: 0, id: [] },
  };
  let total = {
    explicit: 0,
    mainAI: 0,
    mainAIOverhearing: 0,
    pivot: 0,
    random: 0,
  };

  for (let i = 0; i < charts.length; i++) {
    if (charts[i].chartSelection.includes("explicit_point")) {
      chosenCharts.explicit.count++;
      chosenCharts.explicit.id.push(charts[i].id);
    }
    if (charts[i].chartSelection.includes("mainAI_point")) {
      chosenCharts.mainAI.count++;
      chosenCharts.mainAI.id.push(charts[i].id);
    }
    if (charts[i].chartSelection.includes("mainAIOverhearing_point")) {
      chosenCharts.mainAIOverhearing.count++;
      chosenCharts.mainAIOverhearing.id.push(charts[i].id);
    }
    if (charts[i].chartSelection.includes("pivot_point")) {
      chosenCharts.pivot.count++;
      chosenCharts.pivot.id.push(charts[i].id);
    }
    if (charts[i].chartSelection.includes("random_point")) {
      chosenCharts.random.count++;
      chosenCharts.random.id.push(charts[i].id);
    }
  }
  for (let i = 0; i < chartMsg.charts.length; i++) {
    if (chartMsg.charts[i].chartSelection.includes("explicit_point")) {
      total.explicit++;
    }
    if (chartMsg.charts[i].chartSelection.includes("mainAI_point")) {
      total.mainAI++;
    }
    if (chartMsg.charts[i].chartSelection.includes("mainAIOverhearing_point")) {
      total.mainAIOverhearing++;
    }
    if (chartMsg.charts[i].chartSelection.includes("pivot_point")) {
      total.pivot++;
    }
    if (chartMsg.charts[i].chartSelection.includes("random_point")) {
      total.random++;
    }
  }

  return { chosenCharts: chosenCharts, total: total };
}
