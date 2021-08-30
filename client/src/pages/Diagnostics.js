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
function Diagnostics({ chartMsg }) {
  const [transcriptData, setTranscriptData] = useState([]);
  useEffect(() => {
    localStorage.getItem(chartMsg);
  }, [chartMsg]);

  //Download user's data, charts made, looged transcripts,an
  const downloadFile = async () => {
    let myData = {
      transcript: chartMsg.transcript,
      loggedTranscript: chartMsg.loggedTranscript,
      uncontrolledTranscript: chartMsg.uncontrolledTranscript,
      loggedUncontrolledTranscript: chartMsg.loggedUncontrolledTranscript,
      charts: chartMsg.charts,
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
    console.log(words);
    for (let i = 0; i < words.length; i++) {
      let found = false;
      for (let j = 0; j < synonymsAndFeatures.length; j++) {
        for (let w = 0; w < synonymsAndFeatures[j].length; w++) {
          if (words[i].toLowerCase().includes(synonymsAndFeatures[j][w])) {
            tmpTranscriptData.push({ word: words[i], bold: true });
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
            {/* <div>
              <Textarea
                width="40vw"
                height="40vh"
                value={chartMsg.transcript}
                readOnly={true}
              />
            </div> */}
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
                    return <strong>{value.word} </strong>;
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
                  <Text fontWeight="bold">Window + Semantic</Text>

                  <Tr>
                    <Th>Attribute</Th>
                    <Th>Frequency Count</Th>
                  </Tr>
                  {chartMsg.window_semantic.map.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.window_semantic.nominal.map((value, index) => {
                    return (
                      <>
                        <Tr key={index}>
                          <Td> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.window_semantic.quantitative.map((value, index) => {
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
                  <Text fontWeight="bold">Window</Text>

                  <Tr>
                    <Th>Attribute</Th>
                    <Th>Frequency Count</Th>
                  </Tr>
                  {chartMsg.window.map.map((value, index) => {
                    return (
                      <>
                        <Tr>
                          <Td key={index}> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.window.nominal.map((value, index) => {
                    return (
                      <>
                        <Tr key={index}>
                          <Td> {value.header}</Td>
                          <Td> {value.count}</Td>
                        </Tr>
                      </>
                    );
                  })}
                  {chartMsg.window.quantitative.map((value, index) => {
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
              </HStack>
            </div>
          </Box>
        </HStack>
      </Center>
    </>
  );
}

export default Diagnostics;
