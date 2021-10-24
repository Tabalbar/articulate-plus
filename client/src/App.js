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
import listeningImage from "./images/idle.gif";
import talkingImage from "./images/talking.gif";
import muteImage from "./images/mute.gif";
import thinkingImage from "./images/thinking.gif";
import { thinking } from "./components/voice/assistantVoiceOptions";
import AttributeContainer from "./components/staticWindows/AttributeContainer";
import useInterval from "./helpers/useInterval";

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

  //Toggle options for algorithm
  const [modifiedChartOptions, setModifiedChartOptions] = useState(
    JSON.parse(localStorage.getItem("chartOptions")) || {
      useCovidDataset: false,
      sentimentAnalysis: true,
      window: {
        toggle: true,
        pastSentences: 20,
      },
      neuralNetwork: true,
      useSynonyms: true,
      randomCharts: {
        toggle: true,
        minutes: 10,
        chartWindow: 10,
      },
      threshold: 3,
      filter: {
        toggle: true,
        pastSentences: 20,
        threshold: 5,
      },
      pivotCharts: true,
    }
  );

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
    errMsg: [],
    charts: [],
    mainAICount: {
      quantitative: [],
      nominal: [],
      temporal: [],
      map: [],
    },
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
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)];
    setClippyImage(thinkingImage);
    setVoiceMsg(thinkingResponse);

    setShowTooltip(true);

    //Actual request to server
    serverRequest(
      chartMsg,
      setChartMsg,
      modifiedChartOptions,
      setVoiceMsg,
      charts,
      setCharts
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

  //Create charts at a random interval
  useInterval(() => {
    if (modifiedChartOptions.randomCharts.toggle && startStudy) {
      createCharts("random");
    }
  }, modifiedChartOptions.randomCharts.minutes * 60 * 1000);

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
