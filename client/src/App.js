import React, { useState, useEffect } from "react";
import Charts from "./pages/Charts";
import "semantic-ui-css/semantic.min.css";
// import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Diagnostics from "./pages/Diagnostics";
import Dictaphone from "./components/voice/Dictaphone";
import { serverRequest } from "./helpers/serverRequest";
import createDate from "./helpers/createDate";
import { ChakraProvider, VStack } from "@chakra-ui/react";
import { useClippy } from "use-clippy-now";
import { Button, Box, Input, Image, Tooltip } from "@chakra-ui/react";
import { thinking } from "./components/voice/assistantVoiceOptions";
import SideMenu from "./components/sideMenu/SideMenu";
import UseVoice from "./components/voice/UseVoice";
import listeningImage from "./clippyImages/Listening.png";
import muteImage from "./clippyImages/Mute.png";
import thinkingImage from "./clippyImages/Thinking.png";

function App() {
  const [forceUpdate, setForceUpdate] = useState(true);
  const [mute, setMute] = useState(false);
  const [chartsPage, setChartsPage] = useState(true);
  const [charts, setCharts] = useState([]);
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    semanticAnalysis: false,
    window: {
      toggle: true,
      pastSentences: 20,
    },
    neuralNetwork: true,
  });
  const [chartMsg, setChartMsg] = useState(
    JSON.parse(localStorage.getItem("chartMsg")) || {
      command: "",
      attributes: [],
      data: "",
      transcript: "",
      synonymMatrix: [],
      featureMatrix: [],
      currentCharts: [],
      explicitChart: "",
      inferredChart: "",
      modifiedChart: "",
      assistantResponse: "",
      errMsg: [],
      charts: [],
      headerFrequencyCount: {
        quantitative: [],
        nominal: [],
        temporal: [],
        map: [],
      },
    }
  );
  const [clippyImage, setClippyImage] = useState(listeningImage);
  const [voiceMsg, setVoiceMsg] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);
  useEffect(() => {
    if (showTooltip) {
      setTimeout(() => {
        setShowTooltip(false);
      }, 8000);
    }
  }, [showTooltip]);

  useEffect(() => {
    // localStorage.setItem("chartMsg", JSON.stringify(chartMsg));
  }, [chartMsg]);
  const createCharts = (command) => {
    if (command) {
      chartMsg.command = command;
    }
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)];
    setClippyImage(thinkingImage);
    let msg = UseVoice(thinkingResponse, mute);
    setVoiceMsg(thinkingResponse);
    setShowTooltip(true);
    serverRequest(
      chartMsg,
      setChartMsg,
      modifiedChartOptions,
      mute,
      setClippyImage,
      thinkingImage,
      setVoiceMsg
    ).then(() => {
      if (mute) {
        setClippyImage(muteImage);
      } else {
        setClippyImage(listeningImage);
      }
    });
    // msg.onend(() => {
    //   console.log("dne");
    // });
  };
  console.log(chartMsg.charts);
  const chooseChart = (chosenChart) => {
    chosenChart.timeChosen.push(createDate());
    chosenChart.visible = true;
    let found = false;
    for (let i = 0; i < charts.length; i++) {
      if (chosenChart == charts[i]) {
        found = true;
      }
    }
    if (!found) {
      setCharts((prev) => [...prev, chosenChart]);
    } else {
      setForceUpdate((prev) => !prev);
    }

    chartMsg.explicitChart = "";
    chartMsg.inferredChart = "";
    chartMsg.modifiedChart = "";
  };
  const clearCharts = () => {
    localStorage.removeItem("chartMsg");
    localStorage.clear();
  };
  const handleMute = () => {
    setMute((prev) => {
      if (mute) {
        setClippyImage(listeningImage);
      } else {
        setClippyImage(muteImage);
      }
      return !prev;
    });
  };
  const [text, setText] = useState("");

  return (
    <>
      <ChakraProvider>
        <div style={{ display: chartsPage ? null : "None" }}>
          <Box
            position="absolute"
            zIndex={9}
            // bg="red"
            ml={"3rem"}
            width={"14vw"}
            minWidth={"16rem"}
            bottom={"31em"}
          >
            <VStack float="right" spacing={".5px"}>
              <Tooltip
                zIndex="10"
                label={voiceMsg}
                fontSize="3xl"
                placement="right-start"
                isOpen={showTooltip}
                hasArrow
              >
                <Image boxSize="90px" float="right" src={clippyImage} />
              </Tooltip>
              {mute ? (
                <Button
                  width={"5rem"}
                  float={"right"}
                  bg="teal.300"
                  onClick={handleMute}
                >
                  Unmute
                </Button>
              ) : (
                <Button
                  width={"5rem"}
                  float={"right"}
                  bg="teal.300"
                  onClick={handleMute}
                >
                  Mute
                </Button>
              )}
            </VStack>
          </Box>
          <Input
            position="absolute"
            ml="40rem"
            bg="white"
            zIndex={20}
            width={"10rem"}
            onChange={(e) => setText(e.target.value)}
          ></Input>
          <Button
            position="absolute"
            ml={"50rem"}
            zIndex={20}
            onClick={() => createCharts(text)}
          >
            Test
          </Button>
          <Charts
            chartMsg={chartMsg}
            setChartMsg={setChartMsg}
            chooseChart={chooseChart}
            charts={charts}
            setCharts={setCharts}
            mute={mute}
          />

          <SideMenu
            setChartMsg={setChartMsg}
            modifiedChartOptions={modifiedChartOptions}
            setModifiedChartOptions={setModifiedChartOptions}
            chartMsg={chartMsg}
            clearCharts={clearCharts}
          />
        </div>
        <div style={{ display: !chartsPage ? null : "None" }}>
          <Diagnostics chartMsg={chartMsg} mute={mute} />
        </div>
        <Dictaphone
          createCharts={createCharts}
          setChartMsg={setChartMsg}
          chartMsg={chartMsg}
          voiceMsg={voiceMsg}
        />
        <Box position="absolute" top="0" right="0">
          <Button onClick={() => setChartsPage((prev) => !prev)}>
            {chartsPage ? "Diagnostics" : "Charts"}
          </Button>
        </Box>
      </ChakraProvider>
    </>
  );
}

export default App;
