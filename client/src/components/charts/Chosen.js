import React, { useState } from "react";
import "../../style.css";
import Window from "./Window";
import createDate from "../../helpers/createDate";

function ChosenCharts({ charts, chartMsg, setCharts }) {
  const [, setForceUpdate] = useState(true);
  const handleDelete = (index) => {
    setForceUpdate((prev) => !prev);
    charts[index].visible = false;
    charts[index].timeClosed = createDate();
  };

  return (
    <>
      {charts.map((chart, i) => {
        if (chart.visible) {
          return (
            <Window
              specification={chart}
              data={chartMsg.data}
              handleDelete={handleDelete}
              index={i}
              setCharts={setCharts}
              charts={charts}
            />
          );
        } else {
          return null;
        }
      })}
    </>
  );
}

export default ChosenCharts;
