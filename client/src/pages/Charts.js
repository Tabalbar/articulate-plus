import React, { useState } from "react";

//Components
import ChartSelection from "../components/charts/Selection";
import ChosenCharts from "../components/charts/Chosen";

//Helpers
import createDate from "../helpers/createDate";

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
function Charts({
  chartMsg,
  charts,
  setCharts,
  chooseChart,
  mute,
  modifiedChartOptions,
  chartToHighlight,
  globalZIndex,
  setGlobalZIndex,
}) {
  //to Rerender when deleteing charts on chosen charts component
  const [, setForceUpdate] = useState(true);
  //Deleting charts from chosen charts
  const handleDelete = (index) => {
    charts[index].visible = false;
    charts[index].timeClosed.push(createDate());
    charts[index].pivotThis = false;
    setForceUpdate((prev) => !prev);
  };
  const handlePivot = (index) => {
    let tmpCharts = charts;
    tmpCharts[index].pivotThis = !charts[index].pivotThis;

    // charts[index].pivotThis = !charts[index].pivotThis;
    setCharts(tmpCharts);
    setForceUpdate((prev) => !prev);
  };

  return (
    <>
      <ChartSelection
        chartMsg={chartMsg}
        chooseChart={chooseChart}
        mute={mute}
        modifiedChartOptions={modifiedChartOptions}
      />
      <ChosenCharts
        globalZIndex={globalZIndex}
        setGlobalZIndex={setGlobalZIndex}
        handleDelete={handleDelete}
        handlePivot={handlePivot}
        chartMsg={chartMsg}
        charts={charts}
        setCharts={setCharts}
        modifiedChartOptions={modifiedChartOptions}
        chartToHighlight={chartToHighlight}
      />
    </>
  );
}

export default Charts;
