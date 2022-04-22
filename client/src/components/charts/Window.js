import React, { useEffect, useState, useRef } from "react";
import Draggable from "react-draggable";
import { VegaLite } from "react-vega";
import "../../style.css";
import { Box, IconButton, Checkbox } from "@chakra-ui/react";
import { CloseIcon } from "@chakra-ui/icons";
import { useResizeDetector } from "react-resize-detector";
import processData from "../../helpers/processData";
import { keyframes } from "@chakra-ui/system";

function Window(props) {
  const { width, height, ref } = useResizeDetector();
  const [specification, setSpecification] = useState(props.specification);
  const [chartData, setChartData] = useState(props.data);
  const [startTime, setStartTime] = useState(0);
  const resizeTimeout = useRef(null);
  const [highlight, setHighlight] = useState(false);

  const [dragging, setDragging] = useState(false);

  const eventLogger = (e, data) => {
    // let tmpCharts = props.charts;
    // tmpCharts[props.index].x = data.x;
    // tmpCharts[props.index].y = data.y;
    // props.setCharts(tmpCharts);
  };

  const onStart = (e) => {
    e.preventDefault();
    let elems = document.getElementsByClassName("react-draggable");
    //FLAG DISABLED FOR NOW
    // if (props.modifiedChartOptions.pivotCharts && !dragging) {
    //   props.handlePivot(props.index);
    // }
    props.specification.numClicks++;
    console.log("numClicks: ", props.specification.numClicks);
    e.currentTarget.style.zIndex = props.globalZIndex;
    props.setGlobalZIndex((prev) => prev + 1);
  };
  useEffect(() => {
    if (props.chartToHighlight == props.id) {
      setHighlight(true);
    } else {
      setHighlight(false);
    }
  }, [props.chartToHighlight]);

  useEffect(() => {
    if (props.modifiedChartOptions.useCovidDataset == true) {
      if (
        specification.hasOwnProperty("layer") ||
        specification.mark == "bar"
      ) {
        // specification.fetchedURL = true;
        // fetch(
        //   "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
        // )
        //   .then((response) => response.text())
        //   .then(async (csvData) => setChartData(await processData(csvData)));
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

  let pulse = keyframes`
  0% {
    -moz-box-shadow: 0 0 0 0 rgba(204,169,44, 0.4);
    box-shadow: 0 0 0 0 rgba(204,169,44, 0.4);
  }
  50% {
      -moz-box-shadow: 0 0 0 10px rgba(245, 229, 27, 1);
      box-shadow: 0 0 0 30px rgba(245, 229, 27, 1);
  }
  100% {
      -moz-box-shadow: 0 0 0 0 rgba(245, 229, 27, 1);
      box-shadow: 0 0 0 0 rgba(245, 229, 27, 1);
  }
`;

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
        // onStop={eventLogger}
        onDrag={() => setDragging(true)}
        onStop={() =>
          setTimeout(() => {
            setDragging(false);
          }, 500)
        }
      >
        <Box
          position="absolute"
          bg="white"
          overflow="auto"
          boxShadow="2xl"
          ref={ref}
          id={props.id}
          borderColor={props.specification.pivotThis ? "orange" : "black"}
          borderWidth="thin"
          borderRadius="sm"
          borderTopRadius="sm"
          resize="both"
          width={900}
          height={500}
          onMouseOver={startTimer}
          onMouseLeave={endTimer}
          onTouchStart={(e) => onStart(e)}
          onClick={(e) => onStart(e)}
          animation={highlight ? `${pulse} 2s infinite` : null}
          className="react-draggable"
        >
          <div className="handle" style={{ cursor: "move", width: "auto" }}>
            <Box
              borderTopRadius="sm"
              color="white"
              width="full"
              fontWeight="bold"
              bg={props.specification.pivotThis ? "orange.300" : "blue.800"}
              height="full"
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

              {/* {specification.title.text} */}
            </Box>
            <VegaLite spec={specification} data={{ table: chartData }} />
          </div>
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(Window);
