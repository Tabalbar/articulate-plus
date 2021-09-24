import React, { useState } from "react";
import Draggable from "react-draggable";
import "../../style.css";
import {
  Box,
  Accordion,
  AccordionIcon,
  AccordionButton,
  AccordionItem,
  UnorderedList,
  AccordionPanel,
  ListItem,
  Button,
  Center,
  VStack,
  Text,
  Stack,
  Radio,
  Input,
} from "@chakra-ui/react";
import { chartObjState } from "../../shared/chartObjState";
import { useRecoilState } from "recoil";
import ChartObj from "../../shared/ChartObj";
function AttributeContainer({
  setChartMsg,
  modifiedChartOptions,
  setModifiedChartOptions,
  chartMsg,
}) {
  const [start, setStart] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  const eventLogger = (e, data) => {
    console.log(e);
  };

  const onStart = (e) => {
    let elems = document.getElementsByClassName("react-draggable");
    for (let i = 0; i < elems.length; i++) {
      elems[i].style.zIndex = 10;
      e.currentTarget.style.zIndex = 12;
    }
  };
  const handleWindowPastSenteces = (e) => {
    e.preventDefault();
    let pastSentences = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        window: {
          toggle: true,
          pastSentences: parseInt(pastSentences),
        },
      };
    });
  };

  const handleRandomChartsMinutes = (e) => {
    e.preventDefault();
    let numMinutes = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        randomCharts: {
          toggle: true,
          minutes: parseInt(numMinutes),
        },
      };
    });
  };
  const [chart, setChart] = useRecoilState(chartObjState);

  const loadData = async (e) => {
    const response = chart.loadData(e);
    if (response) {
      setDataLoaded(true);
    }
  };
  return (
    <>
      <Draggable
        handle=".handle"
        grid={[1, 1]}
        scale={1}
        defaultPosition={{
          x: 600,
          y: 100,
        }}
        bounds={{ bottom: 1000, left: 0, top: 0 }}
        zIndex={10}
        onStart={onStart.bind(this)}
        onStop={eventLogger}
      >
        <Box
          bg="white"
          position="absolute"
          overflow="auto"
          border="1px"
          boxShadow="2xl"
          borderColor="black"
          borderRadius="sm"
          borderTopRadius="sm"
          onClick={(e) => onStart(e)}
          className="react-draggable"
        >
          <Box
            borderTopRadius="sm"
            color="white"
            width="full"
            fontWeight="bold"
            bg="blue.800"
            height="full"
            p={"3px"}
            onMouseEnter={() => {
              document.body.style.cursor = "grab";
            }}
            onMouseLeave={() => {
              document.body.style.cursor = "default";
            }}
            onMouseDown={() => {
              document.body.style.cursor = "grabbing";
            }}
            onMouseUp={() => {
              document.body.style.cursor = "grab";
            }}
            className="handle"
          >
            {start ? "Attributes" : "Admin"}
          </Box>
          {start ? (
            <>
              <Box
                borderColor="black"
                border="2px"
                zIndex={4}
                width="20rem"
                bg="white"
                overflowY="scroll"
                height="15rem"
                color="black"
                resize="both"
              >
                <Accordion allowMultiple>
                  {ChartObj.attributes.map((value, index) => {
                    return (
                      <AccordionItem>
                        <h2>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              {value}
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                        </h2>
                        <AccordionPanel pb={4}>
                          <UnorderedList>
                            {ChartObj.featureMatrix[index].map(
                              (value, index) => {
                                return index > 0 ? (
                                  <ListItem key={index}>{value}</ListItem>
                                ) : null;
                              }
                            )}
                          </UnorderedList>
                        </AccordionPanel>
                      </AccordionItem>
                    );
                  })}
                </Accordion>
              </Box>
            </>
          ) : (
            <>
              <Input
                bg="white"
                color="black"
                p={1}
                type="file"
                onChange={loadData}
              />

              <Button
                disabled={!dataLoaded}
                colorScheme="teal"
                onClick={() => setStart(true)}
              >
                Start
              </Button>
              {/* <Center>
                <VStack>
                  <FileInput setChartMsg={setChartMsg} />
                  <Text fontWeight="bold" ml={1}>
                    Modified Chart Options
                  </Text>
                  <Stack>
                    <Radio
                      isChecked={ChartObj.options.window.toggle}
                      onClick={() =>
                        setModifiedChartOptions((prev) => {
                          return {
                            ...prev,
                            window: {
                              toggle: !prev.window.toggle,
                              pastSentences: prev.window.pastSentences,
                            },
                          };
                        })
                      }
                      size="lg"
                      colorScheme="teal"
                    >
                      Sentence Window
                    </Radio>
                    {ChartObj.options.window.toggle ? (
                      <Input
                        type="number"
                        value={ChartObj.options.window.pastSentences}
                        onChange={handleWindowPastSenteces}
                      />
                    ) : null}
                    {ChartObj.options.window.toggle ? (
                      <Radio
                        isChecked={ChartObj.options.sentimentAnalysis}
                        onClick={() =>
                          setModifiedChartOptions((prev) => {
                            return {
                              ...prev,
                              sentimentAnalysis: !prev.sentimentAnalysis,
                            };
                          })
                        }
                        size="lg"
                        colorScheme="teal"
                      >
                        Sentiment Analysis
                      </Radio>
                    ) : null}
                    <Radio
                      isChecked={ChartObj.options.neuralNetwork}
                      onClick={() =>
                        setModifiedChartOptions((prev) => {
                          return {
                            ...prev,
                            neuralNetwork: !prev.neuralNetwork,
                          };
                        })
                      }
                      size="lg"
                      colorScheme="teal"
                    >
                      Neural Network (NodeNLP)
                    </Radio>
                    <p>Attribute Threshold Count:</p>
                    <Input
                      type="number"
                      value={modifiedChartOptions.threshold}
                      onChange={handleWindowPastSenteces}
                    />
                    <Radio
                      isChecked={modifiedChartOptions.randomCharts.toggle}
                      onClick={() =>
                        setModifiedChartOptions((prev) => {
                          return {
                            ...prev,
                            randomCharts: {
                              toggle: !prev.randomCharts.toggle,
                              minutes: prev.randomCharts.minutes,
                            },
                          };
                        })
                      }
                      size="lg"
                      colorScheme="teal"
                    >
                      Show Random Charts
                    </Radio>
                    {modifiedChartOptions.randomCharts.toggle ? (
                      <>
                        Minutes:
                        <Input
                          type="number"
                          value={modifiedChartOptions.randomCharts.minutes}
                          onChange={handleRandomChartsMinutes}
                        />
                      </>
                    ) : null}
                  </Stack>

                  <Button
                    disabled={!ChartObj.attributes.length}
                    colorScheme="teal"
                    onClick={() => setStart(true)}
                  >
                    Start
                  </Button>
                </VStack>
              </Center> */}
              <br />
            </>
          )}
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(AttributeContainer);
