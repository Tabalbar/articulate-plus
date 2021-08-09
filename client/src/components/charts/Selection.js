import React, { useEffect, useState } from "react";
import "../../style.css";
import { VegaLite } from "react-vega";
import { Box, HStack } from "@chakra-ui/react";

function ChartSelection({ chartMsg, chooseChart }) {
  return (
    <>
      <Box
        position="absolute"
        bottom="0"
        bg="gray.700"
        width="88vw"
        height="31rem"
        zIndex="1"
        right="0"
        borderTop="2px"
        borderColor="black"
      >
        <Box
          zIndex={3}
          bottom="0"
          width="86vw"
          overflowX="auto"
          display="flex"
          flex={1}
        >
          <HStack spacing={100} display="flex" flexDirection={"row-reverse"}>
            {chartMsg.charts.map((chart, index) => {
              return (
                <>
                  {chart ? (
                    <Box zIndex={20} p={2} key={index}>
                      <ChartPlaceholder
                        specification={chart.charts.spec}
                        data={chartMsg.data}
                        chooseChart={chooseChart}
                      />
                    </Box>
                  ) : null}
                </>
              );
            })}
          </HStack>
        </Box>
      </Box>
    </>
  );
}

function ChartPlaceholder({ specification, data, chooseChart }) {
  const [startTime, setStartTime] = useState("");
  const [spec, setSpec] = useState(specification);
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);
  const [chartData, setChartData] = useState(data);

  specification.x = window.innerWidth / 2;
  specification.y = window.innerHeight / 4;
  useEffect(() => {
    if (specification.hasOwnProperty("layer")) {
      fetch(
        "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
      )
        .then((response) => response.json())
        .then((csvData) => setChartData(csvData));
    }
  }, []);

  const startTimer = () => {
    setStartTime(performance.now());
    setHovered(true);
  };

  const endTimer = () => {
    var timeDiff = performance.now() - startTime;
    timeDiff /= 1000;
    specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2));
    setHovered(false);
  };
  return (
    <>
      <Box
        bg="transparent"
        zIndex={hovered ? 10 : 3}
        onClick={
          specification.visible
            ? null
            : () => {
                endTimer();
                chooseChart(specification);
                setClicked(true);
              }
        }
        onMouseOver={startTimer}
        onMouseLeave={endTimer}
        opacity={specification.visible ? 0.5 : null}
      >
        <Box bg="white" borderColor="black" borderWidth="3px" rounded="lg">
          <VegaLite spec={spec} data={{ table: chartData }} />
        </Box>
      </Box>
    </>
  );
}

export default ChartSelection;