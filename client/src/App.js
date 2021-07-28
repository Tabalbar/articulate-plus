import React, { useState, useEffect } from "react";
import Charts from "./pages/Charts";
import "semantic-ui-css/semantic.min.css";
// import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Diagnostics from "./pages/Diagnostics";
import Dictaphone from "./components/voice/Dictaphone";
import { serverRequest } from "./helpers/serverRequest";
import createDate from "./helpers/createDate";
import { ChakraProvider } from "@chakra-ui/react";
import { useClippy } from "use-clippy-now";
import { Button, Box, Input } from "@chakra-ui/react";
import { thinking } from "./components/voice/assistantVoiceOptions";
import SideMenu from "./components/sideMenu/SideMenu";

function App() {
  const withClippy = useClippy("Links");
  const [mute, setMute] = useState(false);
  const [chartsPage, setChartsPage] = useState(true);
  const [charts, setCharts] = useState([]);
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    semanticAnalysis: true,
    window: {
      toggle: true,
      pastSentences: 999,
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
      headerFrequencyCount: { quantitative: [], nominal: [], temporal: [] },
    }
  );

  useEffect(() => {
    localStorage.setItem("chartMsg", JSON.stringify(chartMsg));
  }, [chartMsg]);

  const createCharts = (command) => {
    if (command) {
      chartMsg.command = command;
    }
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)];
    withClippy((clippy) => clippy.speak(thinkingResponse));
    setTimeout(() => {
      withClippy((clippy) => clippy.play("Processing"));
    }, 1000);

    return serverRequest(
      chartMsg,
      setChartMsg,
      withClippy,
      modifiedChartOptions,
      mute
    );
  };

  const chooseChart = (chosenChart) => {
    chosenChart.timeChosen = createDate();
    chosenChart.visible = true;
    setCharts((prev) => [...prev, chosenChart]);

    chartMsg.explicitChart = "";
    chartMsg.inferredChart = "";
    chartMsg.modifiedChart = "";
  };
  const clearCharts = () => {
    localStorage.removeItem("chartMsg");
  };
  console.log(chartMsg.headerFreq);
  const handleMute = () => {
    setMute((prev) => {
      if (prev) {
        withClippy((clippy) => clippy.play("Greeting"));
      } else {
        withClippy((clippy) => clippy.play("DeepIdleA"));
      }
      return !prev;
    });
  };
  console.log(chartMsg.charts);
  const [text, setText] = useState("");
  return (
    <>
      <ChakraProvider>
        <div style={{ display: chartsPage ? null : "None" }}>
          <Box
            position="absolute"
            zIndex={10}
            width={"15vw"}
            minWidth={"17rem"}
            bottom={"31rem"}
          >
            {mute ? (
              <Button float={"right"} bg="teal.300" onClick={handleMute}>
                Unmute
              </Button>
            ) : (
              <Button float={"right"} bg="teal.300" onClick={handleMute}>
                Mute
              </Button>
            )}
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
          withClippy={withClippy}
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
