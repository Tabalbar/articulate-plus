import React, { useState } from "react";
import Charts from "./pages/Charts";
import 'semantic-ui-css/semantic.min.css'
// import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Diagnostics from './pages/Diagnostics'
import Dictaphone from "./components/voice/Dictaphone";
import { serverRequest } from './helpers/serverRequest'
import createDate from './helpers/createDate'
import { ChakraProvider } from "@chakra-ui/react"
import { useClippy } from "use-clippy-now";
import { Button, Box } from '@chakra-ui/react'
import { thinking } from './components/voice/assistantVoiceOptions'
import UseVoice from './components/voice/UseVoice'
import SideMenu from './components/sideMenu/SideMenu'
import {
  RecoilRoot
} from 'recoil'
import { VegaLite } from 'react-vega'

function App() {

  const withClippy = useClippy("Links");
  const [mute, setMute] = useState(false)
  const [chartsPage, setChartsPage] = useState(true)
  const [charts, setCharts] = useState([])
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    semanticAnalysis: true,
    window: {
      toggle: true,
      pastSentences: 999,
    },
    neuralNetwork: true
  })

  const [chartMsg, setChartMsg] = useState({
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
    charts: []
  })
  // React.useEffect(() => {
  //   fetch("/initialize", )
  //     .then((res) => res.json())
  //     .then((data) => setData(data.message));
  // }, []);

  const createCharts = (command) => {
    console.log(command)

    if (command) {
      chartMsg.command = command
    }
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)]
    withClippy((clippy) => clippy.speak(thinkingResponse))
    withClippy((clippy) => clippy.play("Processing"))

    UseVoice(thinkingResponse, mute)
    serverRequest(chartMsg, setChartMsg, withClippy, modifiedChartOptions, mute)

  }

  const downloadFile = async () => {
    let myData = {
      transcript: chartMsg.transcript,
      charts: chartMsg.charts
    }
    const fileName = "file";
    const json = JSON.stringify(myData);
    const blob = new Blob([json],{type:'application/json'});
    const href = await URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = href;
    link.download = fileName + ".json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  const chooseChart = (chosenChart) => {
    chosenChart.timeChosen = createDate()
    chosenChart.visible = true;
    setCharts(prev => [...prev, chosenChart])

    chartMsg.explicitChart = ""
    chartMsg.inferredChart = ""
    chartMsg.modifiedChart = ""
  }
  const clearCharts = () => {
    setChartMsg(prev=>{
        return {
            ...prev,
            charts: []
        }
    })
}


  return (
    <>
      <RecoilRoot>
        <ChakraProvider>
          
          <Button  mt={10} onClick={downloadFile}>Test</Button>

          {/* <Button onClick={()=>createCharts("Show me a map of uninsured rate")}></Button> */}
          {/* <VegaLite spec={chartSpec} data={{ table: chartMsg.data }} /> */}
          {/* <Router>
          <Switch>
            <Route path="/" exact component={() =>

            } />
            <Route path="/diagnostics" exact component={() =>

            } />
          </Switch>
        </Router> */}
          {/* <Button onClick={()=>UseVoice("speak")}></Button> */}
          <div style={{ display: chartsPage ? null : "None" }}>
            <Charts
              chartMsg={chartMsg}
              setChartMsg={setChartMsg}
              chooseChart={chooseChart}
              charts={charts}
              setCharts={setCharts}
              mute={mute}
              setMute={setMute}
              clearCharts={clearCharts}
            />
          </div>
          <div style={{ display: !chartsPage ? null : "None" }}>
            <Diagnostics
              chartMsg={chartMsg}
            />
          </div>
          <Dictaphone
            createCharts={createCharts}
            setChartMsg={setChartMsg}
            chartMsg={chartMsg}
          />
          <SideMenu
            setChartMsg={setChartMsg}
            modifiedChartOptions={modifiedChartOptions}
            setModifiedChartOptions={setModifiedChartOptions}
          />

          <Box right="0" >
            {/* <Button onClick={() => setChartsPage(prev => !prev)}>{chartsPage ? "Diagnostics" : "Charts"}</Button> */}
          </Box>
        </ChakraProvider>
      </RecoilRoot>
    </>
  );
}

export default App;