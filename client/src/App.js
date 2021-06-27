import React, { useState } from "react";
import Charts from "./pages/Charts";
import 'semantic-ui-css/semantic.min.css'
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Diagnostics from './pages/Diagnostics'
import Dictaphone from "./components/voice/Dictaphone";
import { serverRequest } from './helpers/serverRequest'
import createDate from './helpers/createDate'
import FileInput from './components/charts/FileInput'
import { ChakraProvider } from "@chakra-ui/react"
import { useClippy } from "use-clippy-now";
import { Button, Box } from '@chakra-ui/react'
import {thinking} from './components/voice/assistantVoiceOptions'
import UseVoice from './components/voice/UseVoice'

function App() {

  const [overHearingData, setOverHearingData] = useState('')
  const withClippy = useClippy("Rover");
  const [chartsPage, setChartsPage] = useState(true)
  const [charts, setCharts] = useState([])

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
    if (command) {
      chartMsg.command = command
    }
    let thinkingResponse = thinking[Math.floor(Math.random() * 4)]
    withClippy((clippy) => clippy.play("Searching"))
    withClippy((clippy) => clippy.speak(thinkingResponse))
    UseVoice(thinkingResponse)
    serverRequest(chartMsg, setChartMsg, withClippy)

  }

  const chooseChart = (chosenChart) => {
    chosenChart.timeChosen = createDate()
    chosenChart.visible = true;
    setCharts(prev => [...prev, chosenChart])
    
    chartMsg.explicitChart = ""
    chartMsg.inferredChart = ""
    chartMsg.modifiedChart = ""
  }

  return (
    <>
      <ChakraProvider>
        {/* <Router>
          <Switch>
            <Route path="/" exact component={() =>

            } />
            <Route path="/diagnostics" exact component={() =>

            } />
          </Switch>
        </Router> */}
        <Button onClick={()=>UseVoice("speak")}></Button>
        <div style={{ display: chartsPage ? null : "None" }}>
          <Charts
            setOverHearingData={setOverHearingData}
            overHearingData={overHearingData}
            chartMsg={chartMsg}
            setChartMsg={setChartMsg}
            chooseChart={chooseChart}
            charts={charts}
            setCharts={setCharts}
          />
        </div>
        <div style={{ display: !chartsPage ? null : "None" }}>
          <Diagnostics
            overHearingData={overHearingData}
            chartMsg={chartMsg}
          />
        </div>
        <Dictaphone
          setOverHearingData={setOverHearingData}
          createCharts={createCharts}
          setChartMsg={setChartMsg}
          chartMsg={chartMsg}
        />
        <FileInput
          setChartMsg={setChartMsg}
        />
        <Box  right="0" >
          <Button onClick={() => setChartsPage(prev => !prev)}>{chartsPage ? "Diagnostics" : "Charts"}</Button>
        </Box>
      </ChakraProvider>
    </>
  );
}

export default App;