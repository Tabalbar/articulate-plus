/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
import React, { useState } from "react";

//Components
import ChartSelection from "../components/charts/Selection";
import ChosenCharts from "../components/charts/Chosen";
import { Box } from "@chakra-ui/react";
import { VegaLite } from "react-vega";

//Helpers
import createDate from "../helpers/createDate";

/**
 * handles components for chart selection and chosen charts
 *
 * @param {object} chartMsg State to send to server
 * @param {object} charts Chosen charts
 * @param {function} setCharts set State of chosen charts
 * @param {function} chooseChart handler for choosing a chart
 * @param {boolean} mute for soive synthesizer
 * @returns
 */
function Charts({
  chartMsg,
  charts,
  setCharts,
  chooseChart,
  mute,
  modifiedChartOptions,
  chartToHighlight,
  globalZIndex,
  setGlobalZIndex,
}) {
  //to Rerender when deleteing charts on chosen charts component
  const [, setForceUpdate] = useState(true);
  const [centerChart, setCenterChart] = useState({
    specification: undefined,
    data: undefined,
  });

  //Deleting charts from chosen charts
  const handleDelete = (index) => {
    charts[index].visible = false;
    charts[index].timeClosed.push(createDate());
    charts[index].pivotThis = false;
    setForceUpdate((prev) => !prev);
  };
  const handlePivot = (index) => {
    let tmpCharts = charts;
    tmpCharts[index].pivotThis = !charts[index].pivotThis;

    // charts[index].pivotThis = !charts[index].pivotThis;
    setCharts(tmpCharts);
    setForceUpdate((prev) => !prev);
  };
  console.log(centerChart.specification == undefined, centerChart);
  return (
    <>
      <ChartSelection
        chartMsg={chartMsg}
        chooseChart={chooseChart}
        mute={mute}
        setCenterChart={setCenterChart}
        modifiedChartOptions={modifiedChartOptions}
      />
      <ChosenCharts
        globalZIndex={globalZIndex}
        setGlobalZIndex={setGlobalZIndex}
        handleDelete={handleDelete}
        handlePivot={handlePivot}
        chartMsg={chartMsg}
        charts={charts}
        setCharts={setCharts}
        modifiedChartOptions={modifiedChartOptions}
        chartToHighlight={chartToHighlight}
      />

      {centerChart.specification === undefined ? null : (
        <>
          <Box
            zIndex={globalZIndex}
            pointerEvents="none"
            w="full"
            h="full"
            bg="black"
            opacity={0.2}
            position={"absolute"}
          ></Box>
          <Box
            position={"absolute"}
            transform="scale(2.0)"
            top="30%"
            border={"2px solid black"}
            rounded="lg"
            right="35%"
            bg="white"
            zIndex={globalZIndex + 1}
          >
            <VegaLite
              spec={centerChart.specification}
              data={{ table: centerChart.data }}
            />
          </Box>
        </>
      )}
    </>
  );
}

export default Charts;
