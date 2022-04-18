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

  const [userStudyName, setUserStudyName] = useState("");

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
    pythonCharts: [],
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

  useEffect(() => {
    async function logData() {
      if (startStudy) {
        let content = {
          count: makeCount(charts, chartMsg),
          chosenCharts: charts,
          transcript: chartMsg.transcript,
          loggedTranscript: chartMsg.loggedTranscript,
          uncontrolledTranscript: chartMsg.uncontrolledTranscript,
          loggedUncontrolledTranscript: chartMsg.loggedUncontrolledTranscript,
          charts: chartMsg.charts,
          synonymsAndFeatures: chartMsg.synonymMatrix,
        };
        const response = await fetch("/log", {
          method: "POST",
          body: JSON.stringify({
            fileName: userStudyName,
            content,
          }),
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        });
      }
    }
    logData();
  }, [chartMsg]);

  const [studyName, setStudyName] = useState("");

  // SAVE FILE ON EVERY STATE CHANGE
  useEffect(() => {
    //TODO WRITE SAVE FILE
    if (studyName !== "") {
      // ANY CHANGE TO CHART MESSAGE
      // POST TO NODE SERVER (JSON.stringy(chartMsg), studyName)
    }
  }, [chartMsg, studyName]);

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

    //Actual request to server
    serverRequest(
      chartMsg,
      setChartMsg,
      modifiedChartOptions,
      setVoiceMsg,
      charts,
      setCharts,
      setChartToHighlight
    ).then((response) => {
      if (mute) {
        setClippyImage(muteImage);
      } else {
        //Voice syntheiszer
        if (response.assistantResponse) {
          speakVoice(response.assistantResponse.soundFile);
          setVoiceMsg(response.assistantResponse.msg);
          setClippyImage(talkingImage);
          speakVoice(chartSound);
          setShowTooltip(true);
        }
        setTimeout(() => {
          setClippyImage(listeningImage);
        }, 3000);
      }
      return response.isCommand;
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
          {/* COMMENT THIS WHEN STARTING USER STUDY */}
          {/* <Button onClick={() => speakVoice("This is a message")}>
            Test Voice
          </Button> */}
          <Input
            position="absolute"
            ml="20rem"
            bg="white"
            zIndex={20}
            width={"10rem"}
            ref={textRef}
          ></Input>

          <Button
            position="absolute"
            ml={"30rem"}
            zIndex={20}
            onClick={() => createCharts(textRef.current.value)}
          >
            Test
          </Button>

          {/* <Button
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
          </Button> */}
          {/* COMMENT THIS WHEN STARTING USER STUDY */}

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
            setUserStudyName={setUserStudyName}
            userStudyName={userStudyName}
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
