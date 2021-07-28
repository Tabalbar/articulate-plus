import React from "react";
import ChartSelection from "../components/charts/Selection";
import ChosenCharts from "../components/charts/Chosen";

function Charts({ chartMsg, charts, setCharts, chooseChart, mute }) {
  return (
    <>
      <ChartSelection
        chartMsg={chartMsg}
        chooseChart={chooseChart}
        mute={mute}
      />
      <ChosenCharts chartMsg={chartMsg} charts={charts} setCharts={setCharts} />
    </>
  );
}

export default Charts;
