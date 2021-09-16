import React, { useEffect, useRef, useState } from "react";
import "../../style.css";
import { VegaLite } from "react-vega";
import { Box, HStack, Button, useTimeout } from "@chakra-ui/react";
import processData from "../../helpers/processData";

function ChartSelection({ chartMsg, chooseChart }) {
  const slideTimer = useRef(null);
  useEffect(() => {
    if (slideTimer) {
      clearInterval(slideTimer.current);
    }
    let scrollableElement = document.getElementById("scrollable");
    scrollableElement.scrollLeft =
      scrollableElement.scrollWidth - scrollableElement.clientWidth;
    slideTimer.current = setInterval(() => {
      scrollableElement.scrollLeft += 5;
      if (
        scrollableElement.scrollLeft + scrollableElement.clientWidth >=
        scrollableElement.scrollWidth - 10
      ) {
        clearInterval(slideTimer.current);
      }
    }, 35);
  }, [chartMsg.charts]);

  return (
    <>
      <Box
        position="absolute"
        bottom="0"
        bg="gray.700"
        width="100vw"
        height="31rem"
        zIndex="1"
        right="0"
        borderTop="2px"
        borderColor="black"
      >
        <Box
          zIndex={3}
          bottom="0"
          width="100vw"
          overflowX="auto"
          display="flex"
          id="scrollable"
          flex={1}
        >
          <HStack spacing={100}>
            {chartMsg.charts.map((chart, index) => {
              return (
                <>
                  {chart ? (
                    <Box
                      onMouseEnter={() => {
                        clearInterval(slideTimer.current);
                        let scrollableElement =
                          document.getElementById("scrollable");
                      }}
                      zIndex={20}
                      p={2}
                      key={index}
                    >
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
    if (specification.hasOwnProperty("layer") || specification.mark == "bar") {
      fetch(
        "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
      )
        .then((response) => response.text())
        .then(async (csvData) => setChartData(await processData(csvData)));
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
