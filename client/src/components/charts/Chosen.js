/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
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
  globalZIndex,
  setGlobalZIndex,
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
