import React from "react";
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
