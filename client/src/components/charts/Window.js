import React, { useEffect, useState, useRef } from "react";
import Draggable from "react-draggable";
import { VegaLite } from "react-vega";
import "../../style.css";
import { Box, IconButton, Checkbox } from "@chakra-ui/react";
import { CloseIcon } from "@chakra-ui/icons";
import { useResizeDetector } from "react-resize-detector";
import processData from "../../helpers/processData";

function Window(props) {
  const { width, height, ref } = useResizeDetector();
  const [specification, setSpecification] = useState(props.specification);
  const [chartData, setChartData] = useState(props.data);
  const [startTime, setStartTime] = useState(0);
  const resizeTimeout = useRef(null);

  const eventLogger = (e, data) => {
    // let tmpCharts = props.charts;
    // tmpCharts[props.index].x = data.x;
    // tmpCharts[props.index].y = data.y;
    // props.setCharts(tmpCharts);
  };

  const onStart = (e) => {
    e.preventDefault();
    let elems = document.getElementsByClassName("react-draggable");
    if (props.modifiedChartOptions.pivotCharts) {
      console.log(e);
      props.handlePivot(props.index);
    }
    for (let i = 0; i < elems.length; i++) {
      elems[i].style.zIndex = 10;
      e.currentTarget.style.zIndex = 12;
    }
  };
  useEffect(() => {
    if (props.modifiedChartOptions.useCovidDataset == true) {
      if (
        specification.hasOwnProperty("layer") ||
        specification.mark == "bar"
      ) {
        fetch(
          "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
        )
          .then((response) => response.text())
          .then(async (csvData) => setChartData(await processData(csvData)));
      }
    }
  }, []);
  useEffect(() => {
    if (resizeTimeout.current) {
      clearTimeout(resizeTimeout.current);
    }

    resizeTimeout.current = setTimeout(() => {
      setSpecification((prev) => {
        return {
          ...prev,
          width: parseInt(width) - 250,
          height: parseInt(height) - 200,
        };
      });
    }, 100);
  }, [width, height]);
  const startTimer = () => {
    setStartTime(performance.now());
  };
  const endTimer = () => {
    var timeDiff = performance.now() - startTime;
    timeDiff /= 1000;
    specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2));
  };

  useEffect(() => {
    let elem = document.getElementById(props.id);
    let elems = document.getElementsByClassName("react-draggable");
    for (let i = 0; i < elems.length; i++) {
      elems[i].style.zIndex = 10;
    }
    elem.style.zIndex = 13;
  }, []);
  return (
    <>
      <Draggable
        handle=".handle"
        grid={[1, 1]}
        scale={1}
        bounds={{ bottom: 3000, top: 0 }}
        defaultPosition={{
          x: props.charts[props.index].x,
          y: props.charts[props.index].y,
        }}
        onStop={eventLogger}
      >
        <Box
          position="absolute"
          bg="white"
          overflow="auto"
          border="1px"
          boxShadow="2xl"
          ref={ref}
          id={props.id}
          borderColor={props.specification.pivotThis ? "teal" : "black"}
          borderRadius="sm"
          borderTopRadius="sm"
          resize="both"
          width={900}
          height={500}
          onMouseOver={startTimer}
          onMouseLeave={endTimer}
          onMouse
          onTouchStart={(e) => onStart(e)}
          onClick={(e) => onStart(e)}
          className="react-draggable"
        >
          <div className="handle" style={{ cursor: "move", width: "auto" }}>
            <Box
              borderTopRadius="sm"
              color="white"
              width="full"
              fontWeight="bold"
              bg={props.specification.pivotThis ? "teal.600" : "blue.800"}
              height="full"
              zIndex="13"
              position="relative"
            >
              <IconButton
                colorScheme="red"
                borderRadius="sm"
                aria-label="Search database"
                icon={<CloseIcon />}
                mr={2}
                onTouchStart={(e) => {
                  e.stopPropagation();
                  props.handleDelete(props.index);
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  props.handleDelete(props.index);
                }}
              />

              {specification.title}
            </Box>
            <VegaLite spec={specification} data={{ table: chartData }} />
          </div>
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(Window);
