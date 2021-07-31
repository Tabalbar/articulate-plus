import React from "react";
import {
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Button,
  Text,
  useDisclosure,
  Box,
  IconButton,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionIcon,
  AccordionPanel,
  UnorderedList,
  ListItem,
  Stack,
  Radio,
  Input,
  HStack,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import FileInput from "./FileInput";

function SideMenu({
  setChartMsg,
  modifiedChartOptions,
  setModifiedChartOptions,
  chartMsg,
  clearCharts,
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const btnRef = React.useRef();
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

  return (
    <>
      <Box
        position="absolute"
        minWidth="13rem"
        left="0"
        p={"2rem"}
        height="full"
        width="12vw"
        bg="gray.700"
        color="white"
        zIndex="9"
      >
        <HStack>
          <Text fontWeight="bold" fontSize="lg">
            Admin
          </Text>
          <IconButton
            borderRadius="lg"
            colorScheme="red"
            size="sm"
            aria-label="Search database"
            onClick={clearCharts}
            icon={<DeleteIcon />}
          />
        </HStack>
        <br />
        <br />
        <Text fontWeight="bold" ml={1}>
          Load Dataset
        </Text>
        <FileInput setChartMsg={setChartMsg} />
        <br />
        <br />
        <br />
        <Text fontWeight="bold" ml={1}>
          Modified Chart Options
        </Text>
        <Stack>
          <Radio
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
          </Radio>
          {modifiedChartOptions.window.toggle ? (
            <Input
              bg="white"
              color="black"
              type="number"
              value={modifiedChartOptions.window.pastSentences}
              onChange={handleWindowPastSenteces}
            />
          ) : null}
          {modifiedChartOptions.window.toggle ? (
            <Radio
              isChecked={modifiedChartOptions.semanticAnalysis}
              onClick={() =>
                setModifiedChartOptions((prev) => {
                  return { ...prev, semanticAnalysis: !prev.semanticAnalysis };
                })
              }
              size="lg"
              colorScheme="teal"
            >
              Sentiment Analysis
            </Radio>
          ) : null}

          <Radio
            isChecked={modifiedChartOptions.neuralNetwork}
            onClick={() =>
              setModifiedChartOptions((prev) => {
                return { ...prev, neuralNetwork: !prev.neuralNetwork };
              })
            }
            size="lg"
            colorScheme="teal"
          >
            Neural Network (NodeNLP)
          </Radio>
        </Stack>
        <Box
          borderColor="black"
          border="2px"
          zIndex={4}
          width="10vw"
          bg="white"
          overflowY="scroll"
          height="40vh"
          bottom="0"
          minWidth="8rem"
          position="absolute"
          mb="1rem"
          color="black"
        >
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
                      {chartMsg.featureMatrix[index].map((value, index) => {
                        return index > 0 ? (
                          <ListItem key={index}>{value}</ListItem>
                        ) : null;
                      })}
                    </UnorderedList>
                  </AccordionPanel>
                </AccordionItem>
              );
            })}
          </Accordion>
        </Box>
      </Box>
      <Drawer placement="left" onClose={onClose} finalFocusRef={btnRef}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton
            borderColor="red"
            border="1px"
            color="red"
            variant="outline"
          />
          <DrawerHeader>Admin</DrawerHeader>

          <DrawerBody>
            <Text fontWeight="bold" ml={1}>
              Load Dataset
            </Text>
            <FileInput setChartMsg={setChartMsg} />
            <br />
            <br />
            <br />
            <br />
            <Text fontWeight="bold" ml={1}>
              Modified Chart Options
            </Text>
            <Stack>
              <Radio
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
              </Radio>
              {modifiedChartOptions.window.toggle ? (
                <Input
                  type="number"
                  value={modifiedChartOptions.window.pastSentences}
                  onChange={handleWindowPastSenteces}
                />
              ) : null}
              {modifiedChartOptions.window.toggle ? (
                <Radio
                  isChecked={modifiedChartOptions.semanticAnalysis}
                  onClick={() =>
                    setModifiedChartOptions((prev) => {
                      return {
                        ...prev,
                        semanticAnalysis: !prev.semanticAnalysis,
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
                isChecked={modifiedChartOptions.neuralNetwork}
                onClick={() =>
                  setModifiedChartOptions((prev) => {
                    return { ...prev, neuralNetwork: !prev.neuralNetwork };
                  })
                }
                size="lg"
                colorScheme="teal"
              >
                Neural Network (NodeNLP)
              </Radio>
            </Stack>

            {/**-----------------USED FOR DEBUGGING TRANSCIPRTION------------ */}
            {/* <Textarea value={text} onChange={(e)=>setText(e.target.value)}></Textarea>
                        <Textarea value={transcriptText}></Textarea>
                        <Button onClick={()=>setTranscriptText(text)}></Button> */}
          </DrawerBody>

          <DrawerFooter>
            <Button variant="outline" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue">Save</Button>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </>
  );
}

export default SideMenu;
