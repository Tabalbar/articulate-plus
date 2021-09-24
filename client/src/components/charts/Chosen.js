import React, { useState } from "react";
import "../../style.css";
import Window from "./Window";
import { Box } from "@chakra-ui/react";
import ChartObj from "../../shared/ChartObj";

function ChosenCharts({
  chosenCharts,
  setChosenCharts,
  chartMsg,
  setCharts,
  handleDelete,
}) {
  return (
    <>
      {chosenCharts.map((chart, i) => {
        if (chart.visible) {
          return (
            <Window
              specification={chart}
              data={ChartObj.data}
              handleDelete={handleDelete}
              index={i}
              key={i}
              setChosenCharts={setChosenCharts}
              chosenCharts={chosenCharts}
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
