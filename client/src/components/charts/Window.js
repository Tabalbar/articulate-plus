import React from "react";
import Draggable from "react-draggable";
import { VegaLite } from "react-vega";
import "../../style.css";
import { Box, IconButton } from "@chakra-ui/react";
import { CloseIcon } from "@chakra-ui/icons";

function Window(props) {
  const eventLogger = (e, data) => {
    let tmpCharts = props.charts;
    tmpCharts[props.index].x = data.x;
    tmpCharts[props.index].y = data.y;
    props.setCharts(tmpCharts);
  };

  const onStart = (e) => {
    let elems = document.getElementsByClassName("react-draggable");
    for (let i = 0; i < elems.length; i++) {
      elems[i].style.zIndex = 10;
      e.currentTarget.style.zIndex = 12;
    }
  };

  return (
    <>
      <Draggable
        handle=".handle"
        grid={[1, 1]}
        scale={1}
        bounds={{ bottom: 510, left: 0 }}
        defaultPosition={{
          x: props.charts[props.index].x,
          y: props.charts[props.index].y,
        }}
        onStart={onStart.bind(this)}
        onStop={eventLogger}
      >
        <Box
          position="absolute"
          bg="white"
          overflow="auto"
          border="1px"
          boxShadow="2xl"
          borderColor="black"
          borderRadius="sm"
          resize="both"
          width={900}
          height={500}
        >
          <div className="handle" style={{ cursor: "move", width: "auto" }}>
            <Box borderTopRadius="sm" bg="teal.800" height="full">
              <IconButton
                colorScheme="red"
                borderRadius="sm"
                aria-label="Search database"
                icon={<CloseIcon />}
                onClick={() => props.handleDelete(props.index)}
              />
            </Box>
            <VegaLite
              // width={width - 200}
              // height={height - 200}
              spec={props.specification}
              data={{ table: props.data }}
            />
          </div>
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(Window);
