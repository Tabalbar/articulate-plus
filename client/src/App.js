import React, { useEffect, useState } from "react";
import Charts from "./pages/Charts";
import 'semantic-ui-css/semantic.min.css'
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Diagnostics from './pages/Diagnostics'
import Dictaphone from "./components/voice/Dictaphone";
import { serverRequest } from './helpers/serverRequest'

function App() {
  const [overHearingData, setOverHearingData] = useState('')
  const [chartMsg, setChartMsg] = useState({
    command: "",
    attributes: [],
    data: "",
    transcript: "",
    synonymMatrix: [],
    featureMatrix: [],
    currentCharts: [],
    explicitChart: "",
    frequencyChart: "",
    windowChart: "",
    assistantResponse: "",
    errMsg: []
})
  // React.useEffect(() => {
  //   fetch("/initialize", )
  //     .then((res) => res.json())
  //     .then((data) => setData(data.message));
  // }, []);
  const createCharts = (command) => {
    if(command) {
      chartMsg.command = command
    }
    serverRequest(chartMsg, setChartMsg)
  }
  const [charts, setCharts] = useState([])
  const chooseChart = (chosenChart) => {
    setCharts(prev=>[...prev, chosenChart])
    chartMsg.explicitChart = ""
    chartMsg.frequencyChart = ""
    chartMsg.windowChart = ""

} 
  return (
    <>
      <div className="App">
        <Router>
          <Switch>
            <Route path="/" exact component={() =>
              <Charts
                setOverHearingData={setOverHearingData}
                overHearingData={overHearingData}
                chartMsg={chartMsg}
                setChartMsg={setChartMsg}
                chooseChart={chooseChart}
                charts={charts}
              />
            } />
            <Route path="/diagnostics" exact component={() =>
              <Diagnostics
                overHearingData={overHearingData}
              />
            } />
          </Switch>
        </Router>
        <Dictaphone
                setOverHearingData={setOverHearingData}
                createCharts={createCharts}
                setChartMsg={setChartMsg}
            />
      </div>
    </>
  );
}

export default App;