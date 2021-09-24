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
import AttributeContainer from "./components/staticWindows/AttributeContainer";
import ChartObj from "./shared/ChartObj";

import { RecoilRoot, atom, selector, useRecoilState } from "recoil";

import { chartObjState } from "./shared/chartObjState";

function App() {
  const [, setForceUpdate] = useState(true);

  //Mute for synthesizer
  const [mute, setMute] = useState(false);

  // State for dashboard or diagnostics page
  const [chartsPage, setChartsPage] = useState(true);

  //Charts held in Chosen component
  const [charts, setCharts] = useState([]);

  //Toggle options for algorithm

  //Visual feedback for computer unuted, mute, and thinking
  const [clippyImage, setClippyImage] = useState(listeningImage);

  const [voiceMsg, setVoiceMsg] = useState(null);

  const randomChartIntervalId = useRef(null);

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

  useEffect(() => {
    if (ChartObj.options.randomCharts.toggle) {
      randomChartIntervalId.current = setInterval(() => {
        ChartObj.serverRequest("");
      }, ChartObj.options.randomCharts.minutes * 60 * 1000);
    } else {
      clearInterval(randomChartIntervalId.current);
    }
  }, [ChartObj.options.randomCharts.toggle]);

  //In chartSelection component, handles choosing the chart to add in
  //Chosen component

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
      <RecoilRoot>
        <ChakraProvider>
          <div style={{ display: chartsPage ? null : "None" }}>
            {/* <Input
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
              onClick={() => ChartObj.serverRequest(textRef.current.value)}
            >
              Test
            </Button> */}
            {/* <ArtyContainer
              clippyImage={clippyImage}
              handleMute={handleMute}
              clearCharts={clearCharts}
              voiceMsg={voiceMsg}
              mute={mute}
              showTooltip={showTooltip}
            /> */}
            <AttributeContainer />

            <Charts charts={charts} setCharts={setCharts} mute={mute} />
          </div>
          <div style={{ display: !chartsPage ? null : "None" }}>
            {/* <Diagnostics mute={mute} /> */}
          </div>
          {/* <Dictaphone voiceMsg={voiceMsg} mute={mute} />
          <Box position="absolute" top="0" right="0">
            <Button onClick={() => setChartsPage((prev) => !prev)}>
              {chartsPage ? "Diagnostics" : "Charts"}
            </Button>
          </Box> */}
        </ChakraProvider>
      </RecoilRoot>
    </>
  );
}

export default App;
