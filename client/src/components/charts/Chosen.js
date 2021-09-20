import React, { useState } from "react";
import "../../style.css";
import Window from "./Window";
import { Box } from "@chakra-ui/react";

function ChosenCharts({ charts, chartMsg, setCharts, handleDelete }) {
  return (
    <>
      {/* <Box
        position="absolute"
        right={0}
        width="100vw"
        height="52vw"
        bg="red"
        zIndex={0}
      > */}
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
      {/* </Box> */}
    </>
  );
}

export default ChosenCharts;
