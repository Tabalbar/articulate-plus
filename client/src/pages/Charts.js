import React, { useState } from "react";

//Components
import ChartSelection from "../components/charts/Selection";
import ChosenCharts from "../components/charts/Chosen";

//Helpers
import createDate from "../helpers/createDate";
import { chartObjState } from "../shared/chartObjState";
import { useRecoilValue } from "recoil";
/**
 * handles components for chart selection and chosen charts
 *
 * @param {object} chartMsg State to send to server
 * @param {object} charts Chosen charts
 * @param {function} setCharts set State of chosen charts
 * @param {function} chooseChart handler for choosing a chart
 * @param {boolean} mute for soive synthesizer
 * @returns
 */
function Charts({ chartMsg, charts, setCharts, mute }) {
  const chartObj = useRecoilValue(chartObjState);
  const [chosenCharts, setChosenCharts] = useState([]);
  //to Rerender when deleteing charts on chosen charts component
  const [, setForceUpdate] = useState(true);
  //Deleting charts from chosen charts
  const handleDelete = (index) => {
    charts[index].visible = false;
    charts[index].timeClosed.push(createDate());
    setForceUpdate((prev) => !prev);
  };
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
      setChosenCharts((prev) => [...prev, chosenChart]);
    } else {
      setForceUpdate((prev) => !prev);
    }

    chartObj.explicitChart = "";
    chartObj.inferredChart = "";
    chartObj.modifiedChart = "";
  };
  return (
    <>
      <ChartSelection
        chartMsg={chartMsg}
        chooseChart={chooseChart}
        mute={mute}
      />
      <ChosenCharts
        handleDelete={handleDelete}
        chartMsg={chartMsg}
        chosenCharts={chosenCharts}
        setCharts={setCharts}
      />
    </>
  );
}

export default Charts;
