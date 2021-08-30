import React, { useState, useEffect, useRef } from "react";
import "semantic-ui-css/semantic.min.css";

//Pages
import Diagnostics from "./pages/Diagnostics";
import Charts from "./pages/Charts";

//Components
import Dictaphone from "./components/voice/Dictaphone";
import SideMenu from "./components/sideMenu/SideMenu";

//Helper functions
import { serverRequest } from "./helpers/serverRequest";
import createDate from "./helpers/createDate";

import {
  ChakraProvider,
  VStack,
  Button,
  Box,
  Input,
  Image,
  Tooltip,
} from "@chakra-ui/react";

//For computer talking
import listeningImage from "./images/idle.gif";
import talkingImage from "./images/talking.gif";
import muteImage from "./images/mute.gif";
import thinkingImage from "./images/thinking.gif";
import { thinking } from "./components/voice/assistantVoiceOptions";

function App() {
  const [, setForceUpdate] = useState(true);

  //Mute for synthesizer
  const [mute, setMute] = useState(false);

  // State for dashboard or diagnostics page
  const [chartsPage, setChartsPage] = useState(true);

  //Charts held in Chosen component
  const [charts, setCharts] = useState([]);

  //Toggle options for algorithm
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    semanticAnalysis: false,
    window: {
      toggle: true,
      pastSentences: 20,
    },
    neuralNetwork: true,
  });

  // Chart message to send to server
  const [chartMsg, setChartMsg] = useState(
    JSON.parse(localStorage.getItem("chartMsg")) || {
      command: "", //Query
      attributes: [],
      data: "",
      transcript: "",
      uncontrolledTranscript: "",
      loggedTranscript: [], // {sentence: string, date: createDate()}
      loggedUncontrolledTranscript: [],
      synonymMatrix: [], //Synonyms used in attributes
      featureMatrix: [], //Unique data values
      currentCharts: [],
      explicitChart: "",
      inferredChart: "",
      modifiedChart: "",
      assistantResponse: "",
      errMsg: [],
      charts: [],
      window_semantic: {
        quantitative: [],
        nominal: [],
        temporal: [],
        map: [],
      },
      window: {
        quantitative: [],
        nominal: [],
        temporal: [],
        map: [],
      },
    }
  );

  //Visual feedback for computer unuted, mute, and thinking
  const [clippyImage, setClippyImage] = useState(listeningImage);

  const [voiceMsg, setVoiceMsg] = useState(null);

  // Handler to show thought bubble for clippy
  const [showTooltip, setShowTooltip] = useState(false);
  useEffect(() => {
    if (showTooltip) {
      setTimeout(() => {
        setShowTooltip(false);
      }, 8000);
    }
  }, [showTooltip]);

  // Handle Request to server
  const createCharts = (command) => {
    if (command) {
      chartMsg.command = command;
    }
    //Pick a random thinking response
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)];
    setClippyImage(thinkingImage);
    setVoiceMsg(thinkingResponse);

    setShowTooltip(true);

    //Actual request to server
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
        setClippyImage(talkingImage);
        setTimeout(() => {
          setClippyImage(listeningImage);
        }, 3000);
      }
    });
  };

  //In chartSelection component, handles choosing the chart to add in
  //Chosen component
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
  const textRef = useRef("");

  return (
    <>
      <ChakraProvider>
        <div style={{ display: chartsPage ? null : "None" }}>
          {/* <Box
            position="absolute"
            zIndex={9}
            // bg="red"
            zIndex="10"
            width={"14vw"}
            minWidth={"16rem"}
            bottom={"31em"}
          >
            <VStack spacing={".5px"}>
              <Tooltip
                zIndex="10"
                label={voiceMsg}
                fontSize="3xl"
                placement="right-start"
                isOpen={showTooltip}
                hasArrow
              >
                <Image ml="3rem" src={clippyImage} />
              </Tooltip>
              {mute ? (
                <Button width={"10rem"} bg="teal.300" onClick={handleMute}>
                  Not Listening
                </Button>
              ) : (
                <Button width={"10rem"} bg="teal.300" onClick={handleMute}>
                  Listening
                </Button>
              )}
            </VStack>
          </Box> */}
          <Input
            position="absolute"
            ml="40rem"
            bg="white"
            zIndex={20}
            width={"10rem"}
            ref={textRef}
          ></Input>
          <Button
            position="absolute"
            ml={"50rem"}
            zIndex={20}
            onClick={() => createCharts(textRef.current.value)}
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
            clippyImage={clippyImage}
            handleMute={handleMute}
            clearCharts={clearCharts}
            voiceMsg={voiceMsg}
            mute={mute}
            showTooltip={showTooltip}
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
          mute={mute}
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
