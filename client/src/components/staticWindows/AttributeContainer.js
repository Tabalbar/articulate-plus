import React, { useEffect, useState } from "react";
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
import FileInput from "./FileInput";

function AttributeContainer({
  setChartMsg,
  modifiedChartOptions,
  setModifiedChartOptions,
  chartMsg,
  startStudy,
  setStartStudy,
  setUserStudyName,
  userStudyName,
}) {
  const eventLogger = (e, data) => {};
  useEffect(() => {
    if (startStudy) {
      localStorage.setItem(
        "chartOptions",
        JSON.stringify(modifiedChartOptions)
      );
      setChartMsg((prev) => {
        return { ...prev, deltaTime: new Date() };
      });
    }
  }, [startStudy]);

  // const onStart = (e) => {
  //   let elems = document.getElementsByClassName("react-draggable");
  //   for (let i = 0; i < elems.length; i++) {
  //     elems[i].style.zIndex = 10;
  //     e.currentTarget.style.zIndex = 12;
  //   }
  // };

  const handleWindowPastSenteces = (e) => {
    e.preventDefault();
    let pastSentences = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        window: {
          ...prev.window,
          pastSentences: parseInt(pastSentences),
        },
      };
    });
  };

  const handleWindowThreshold = (e) => {
    e.preventDefault();
    let threshold = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        threshold: parseInt(threshold),
      };
    });
  };

  const handleFilterPastSentences = (e) => {
    e.preventDefault();
    let pastSentences = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        filter: {
          ...prev.filter,
          pastSentences: parseInt(pastSentences),
        },
      };
    });
  };

  const handleFilterThreshold = (e) => {
    e.preventDefault();
    let threshold = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        filter: {
          ...prev.filter,
          threshold: parseInt(threshold),
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
          chartWindow: prev.randomCharts.chartWindow,
          minutes: parseInt(numMinutes),
        },
      };
    });
  };

  const handleRandomChartWindow = (e) => {
    e.preventDefault();
    let numWindow = e.target.value;

    setModifiedChartOptions((prev) => {
      return {
        ...prev,
        randomCharts: {
          toggle: true,
          minutes: prev.randomCharts.minutes,
          chartWindow: parseInt(numWindow),
        },
      };
    });
  };
  return (
    <>
      <Draggable
        handle=".handle"
        grid={[1, 1]}
        scale={1}
        defaultPosition={{
          x: window.innerWidth / 2.2,
          y: window.innerHeight / 6,
        }}
        bounds={{ bottom: 1000, left: 0, top: 0 }}
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
          zIndex={200}
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
            {startStudy ? `${chartMsg.datasetTitle} Attributes` : "Admin"}
          </Box>
          {startStudy ? (
            <>
              <Box className="scrollBar">
                <Accordion allowMultiple>
                  {chartMsg.attributes.map((value, index) => {
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
                            {chartMsg.featureMatrix[index].map(
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
              <Center>
                <VStack>
                  <Text>User Study File Name:</Text>
                  <Input
                    onChange={(e) => setUserStudyName(e.target.value)}
                    value={userStudyName}
                  />
                  <FileInput
                    setChartMsg={setChartMsg}
                    setModifiedChartOptions={setModifiedChartOptions}
                    modifiedChartOptions={modifiedChartOptions}
                  />
                  <Text fontWeight="bold" ml={1}>
                    Modified Chart Options
                  </Text>
                  <Stack>
                    <Text>
                      Sentence Window Size (Attributes):{" "}
                      {modifiedChartOptions.window.pastSentences}
                    </Text>
                    <Text>
                      Sentence Window Threshold (Attributes):{" "}
                      {modifiedChartOptions.threshold}
                    </Text>
                    <Text>
                      Past Charts to compare with random:{" "}
                      {modifiedChartOptions.randomCharts.chartWindow}
                    </Text>
                    <Text>
                      Sentence Window Size (Filters):{" "}
                      {modifiedChartOptions.filter.pastSentences}
                    </Text>
                    <Text>
                      Sentence Window Threshold (Filters):{" "}
                      {modifiedChartOptions.filter.threshold}
                    </Text>
                    <Text>
                      Using Pivot: {modifiedChartOptions.pivot ? "Yes" : "No"}
                    </Text>
                    {/* FLAG DISABLED FOR NOW */}
                    {/* <Radio
                      isChecked={modifiedChartOptions.window.toggle}
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
                    </Radio> */}
                    {/* {modifiedChartOptions.window.toggle ? (
                      <>
                        Size of Sentence Window
                        <Input
                          type="number"
                          value={modifiedChartOptions.window.pastSentences}
                          onChange={handleWindowPastSenteces}
                        />
                      </>
                    ) : null} */}
                    {/* {modifiedChartOptions.window.toggle ? (
                      <Radio
                        isChecked={modifiedChartOptions.sentimentAnalysis}
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
                    ) : null} */}
                    {/* <Radio
                      isChecked={modifiedChartOptions.neuralNetwork}
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
                    </Radio> */}
                    {/* <Input
                      type="number"
                      value={modifiedChartOptions.threshold}
                      onChange={handleWindowThreshold}
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
                    </Radio> */}
                    {/* {modifiedChartOptions.randomCharts.toggle ? (
                      <>
                        Minutes:
                        <Input
                          type="number"
                          value={modifiedChartOptions.randomCharts.minutes}
                          onChange={handleRandomChartsMinutes}
                        />
                      </>
                    ) : null} */}
                    {/* {modifiedChartOptions.randomCharts.toggle ? (
                      <>
                        Past Charts to compare with random:
                        <Input
                          type="number"
                          value={modifiedChartOptions.randomCharts.chartWindow}
                          onChange={handleRandomChartWindow}
                        />
                      </>
                    ) : null} */}
                    {/* <Radio
                      isChecked={modifiedChartOptions.filter.toggle}
                      onClick={() =>
                        setModifiedChartOptions((prev) => {
                          return {
                            ...prev,
                            filter: {
                              ...prev.filter,

                              toggle: !prev.filter.toggle,
                            },
                          };
                        })
                      }
                      size="lg"
                      colorScheme="teal"
                    >
                      Filter Sentence Window
                    </Radio>
                    {modifiedChartOptions.filter.toggle ? (
                      <>
                        Filter Threshold:
                        <Input
                          type="number"
                          value={modifiedChartOptions.filter.threshold}
                          onChange={handleFilterThreshold}
                        />
                        Size of Sentence Window
                        <Input
                          type="number"
                          value={modifiedChartOptions.filter.pastSentences}
                          onChange={handleFilterPastSentences}
                        />
                      </>
                    ) : null}
                    <Radio
                      isChecked={modifiedChartOptions.pivotCharts}
                      onClick={() =>
                        setModifiedChartOptions((prev) => {
                          return {
                            ...prev,
                            pivotCharts: !prev.pivotCharts,
                          };
                        })
                      }
                      size="lg"
                      colorScheme="teal"
                    >
                      Use Pivot
                    </Radio> */}
                  </Stack>

                  <Button
                    disabled={!chartMsg.attributes.length}
                    colorScheme="teal"
                    onClick={() => setStartStudy(true)}
                  >
                    Start
                  </Button>
                </VStack>
              </Center>
              <br />
            </>
          )}
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(AttributeContainer);
