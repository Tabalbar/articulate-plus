import React from "react";
import "../../style.css";
import Window from "./Window";

function ChosenCharts({ charts, chartMsg, setCharts, handleDelete }) {
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
              key={i}
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
