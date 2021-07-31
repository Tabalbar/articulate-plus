import React, { useState } from "react";
import "../../style.css";
import Window from "./Window";
import createDate from "../../helpers/createDate";
import { Box } from "@chakra-ui/react";

function ChosenCharts({ charts, chartMsg, setCharts }) {
  const [, setForceUpdate] = useState(true);
  const handleDelete = (index) => {
    setForceUpdate((prev) => !prev);
    charts[index].visible = false;
    charts[index].timeClosed.push(createDate());
    charts.splice(index, 1);
  };
  // console.log(charts);
  return (
    <>
      <Box position="absolute" right={0} width="88vw" height="42vw">
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
      </Box>
    </>
  );
}

export default ChosenCharts;
