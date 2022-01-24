import React, { useState, useEffect, useRef } from "react";
import "semantic-ui-css/semantic.min.css";

//Pages
import Diagnostics from "./pages/Diagnostics";
import Charts from "./pages/Charts";

//Components
import Dictaphone from "./components/voice/Dictaphone";
import ArtyContainer from "./components/staticWindows/ArtyContainer";

//Helper functions
import { serverRequest } from "./helpers/serverRequest";
import createDate from "./helpers/createDate";

import { ChakraProvider, Button, Box, Input } from "@chakra-ui/react";

//For computer talking
import listeningImage from "./images/idle-small.gif";
import talkingImage from "./images/talking-small.gif";
import muteImage from "./images/mute-small.gif";
import thinkingImage from "./images/thinking-small.gif";
import { thinking } from "./components/voice/assistantVoiceOptions";
import AttributeContainer from "./components/staticWindows/AttributeContainer";
import useInterval from "./helpers/useInterval";
import chartSound from "./sounds/chartSound.wav";

import { commandChecker } from "./helpers/commandChecker";
import speakVoice from "./components/voice/speakVoice";

function App() {
  //Start Dictaphone to start listening
  const [startStudy, setStartStudy] = useState(false);

  const [, setForceUpdate] = useState(true);

  //Mute for synthesizer
  const [mute, setMute] = useState(false);

  // State for dashboard or diagnostics page
  const [chartsPage, setChartsPage] = useState(true);

  //Charts held in Chosen component
  const [charts, setCharts] = useState([]);

  const [chartToHighlight, setChartToHighlight] = useState(null);

  //Toggle options for algorithm
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    useCovidDataset: false,
    sentimentAnalysis: true,
    window: {
      toggle: true,
      pastSentences: 5,
    },
    neuralNetwork: true,
    useSynonyms: true,
    randomCharts: {
      toggle: true,
      minutes: 5,
      chartWindow: 0,
    },
    threshold: 2,
    filter: {
      toggle: true,
      pastSentences: 5,
      threshold: 2,
    },
    pivotCharts: true,
  });
  // Chart message to send to server
  const [chartMsg, setChartMsg] = useState({
    command: "", //Query
    attributes: [],
    data: "",
    transcript: "",
    uncontrolledTranscript: "",
    datasetTitle: "",
    loggedTranscript: [], // {sentence: string, date: createDate()}
    loggedUncontrolledTranscript: [],
    synonymMatrix: [], //Synonyms used in attributes
    featureMatrix: [], //Unique data values
    explicitChart: [],
    randomCharts: [],
    mainAI: [],
    mainAIOverhearing: [],
    pivotChart: [],
    deltaTime: 0,
    assistantResponse: "",
    errMsg: "",
    charts: [],
    mainAIOverhearingCount: {
      quantitative: [],
      nominal: [],
      temporal: [],
      map: [],
    },
    total: {
      quantitative: [],
      nominal: [],
      temporal: [],
      map: [],
    },
  });
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
    // let thinkingResponse =
    //   thinking[Math.floor(Math.random() * thinking.length)];
    // setClippyImage(thinkingImage);
    // if (command !== "random") {
    //   speakVoice(thinkingResponse.soundFile);
    //   setVoiceMsg(thinkingResponse.msg);
    // }
    setClippyImage(thinkingImage);
    speakVoice(chartSound);

    //Actual request to server
    serverRequest(
      chartMsg,
      setChartMsg,
      modifiedChartOptions,
      setVoiceMsg,
      charts,
      setCharts,
      setChartToHighlight
    ).then((assistantResponse) => {
      if (mute) {
        setClippyImage(muteImage);
      } else {
        //Voice syntheiszer
        if (assistantResponse) {
          speakVoice(assistantResponse.soundFile);
          setVoiceMsg(assistantResponse.msg);
          setClippyImage(talkingImage);
          setShowTooltip(true);
        }
        setTimeout(() => {
          setClippyImage(listeningImage);
        }, 3000);
      }
    });
  };

  useEffect(() => {
    if (mute) {
      setClippyImage(muteImage);
    } else {
      setTimeout(() => {
        setClippyImage(listeningImage);
      }, 4000);
    }
  }, [clippyImage]);
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

    chartMsg.explicitChart = [];
    chartMsg.mainAI = [];
    chartMsg.mainAIOverhearing = [];
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

  const closeChosenCharts = () => {
    for (let i = 0; i < charts.length; i++) {
      charts[i].visible = false;
      charts[i].pivotThis = false;
    }
    setForceUpdate((prev) => !prev);
  };

  return (
    <>
      <ChakraProvider>
        <div style={{ display: chartsPage ? null : "None" }}>
          <Button onClick={() => speakVoice("This is a message")}>
            Test Voice
          </Button>
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
          <Button
            position="absolute"
            ml={"60rem"}
            zIndex={20}
            onClick={() =>
              commandChecker(
                chartMsg,
                modifiedChartOptions,
                setVoiceMsg,
                charts,
                setChartMsg
              )
            }
          >
            Command Checker
          </Button>
          <ArtyContainer
            clippyImage={clippyImage}
            handleMute={handleMute}
            voiceMsg={voiceMsg}
            mute={mute}
            showTooltip={showTooltip}
          />
          <AttributeContainer
            setChartMsg={setChartMsg}
            modifiedChartOptions={modifiedChartOptions}
            setModifiedChartOptions={setModifiedChartOptions}
            chartMsg={chartMsg}
            setStartStudy={setStartStudy}
            startStudy={startStudy}
          />

          <Charts
            chartMsg={chartMsg}
            setChartMsg={setChartMsg}
            chooseChart={chooseChart}
            charts={charts}
            setCharts={setCharts}
            mute={mute}
            chartToHighlight={chartToHighlight}
            modifiedChartOptions={modifiedChartOptions}
          />
        </div>
        <div style={{ display: !chartsPage ? null : "None" }}>
          <Diagnostics chartMsg={chartMsg} mute={mute} charts={charts} />
        </div>
        <Dictaphone
          createCharts={createCharts}
          setChartMsg={setChartMsg}
          chartMsg={chartMsg}
          voiceMsg={voiceMsg}
          closeChosenCharts={closeChosenCharts}
          mute={mute}
          startStudy={startStudy}
          setClippyImage={setClippyImage}
          setShowTooltip={setShowTooltip}
          setVoiceMsg={setVoiceMsg}
          modifiedChartOptions={modifiedChartOptions}
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
