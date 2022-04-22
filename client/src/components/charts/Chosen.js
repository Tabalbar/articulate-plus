import React, { useState } from "react";
import "../../style.css";
import Window from "./Window";

function ChosenCharts({
  charts,
  chartMsg,
  setCharts,
  handleDelete,
  modifiedChartOptions,
  handlePivot,
  chartToHighlight,
}) {
  const [globalZIndex, setGlobalZIndex] = useState(1);
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
              globalZIndex={globalZIndex}
              setGlobalZIndex={setGlobalZIndex}
              setCharts={setCharts}
              charts={charts}
              handlePivot={handlePivot}
              id={chart.id}
              modifiedChartOptions={modifiedChartOptions}
              chartToHighlight={chartToHighlight}
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
