import React, { useState } from "react";
import ChartSelection from "../components/charts/Selection";
import ChosenCharts from "../components/charts/Chosen";
import createDate from "../helpers/createDate";

function Charts({ chartMsg, charts, setCharts, chooseChart, mute }) {
  const [, setForceUpdate] = useState(true);
  const handleDelete = (index) => {
    charts[index].visible = false;
    charts[index].timeClosed.push(createDate());

    setForceUpdate((prev) => !prev);
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
        charts={charts}
        setCharts={setCharts}
      />
    </>
  );
}

export default Charts;
