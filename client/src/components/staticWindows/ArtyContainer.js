import React, { useEffect } from "react";
import Draggable from "react-draggable";
import "../../style.css";
import { Box, VStack, Tooltip, Image, Button } from "@chakra-ui/react";

function ArtyContainer({
  clippyImage,
  handleMute,
  voiceMsg,
  mute,
  showTooltip,
}) {
  const eventLogger = (e, data) => {
    console.log(e);
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
        defaultPosition={{
          x: window.innerWidth - 200,
          y: window.innerHeight / 2,
        }}
        bounds={{ bottom: 1000, left: 0, top: 0 }}
        zIndex={12}
        onStart={onStart.bind(this)}
        onStop={eventLogger}
      >
        <Box
          position="absolute"
          onClick={(e) => onStart(e)}
          className="react-draggable"
        >
          <div
            className="handle"
            style={{
              cursor: "move",
              zIndex: 10,
            }}
          >
            <VStack>
              <Tooltip
                zIndex="10"
                label={voiceMsg}
                fontSize="3xl"
                placement="left-start"
                isOpen={showTooltip}
                bg="green.600"
                hasArrow
              >
                <Image
                  ml={"3rem"}
                  boxSize="10rem"
                  className="handle"
                  src={clippyImage}
                  draggable="false"
                  userSelect="none"
                />
              </Tooltip>
              {mute ? (
                <Button
                  width={"8rem"}
                  bg="teal.400"
                  color="black"
                  onClick={handleMute}
                  onTouchStart={handleMute}

                >
                  Wake
                </Button>
              ) : (
                <Button
                  width={"8rem"}
                  bg="teal.200"
                  color="black"
                  onClick={handleMute}
                  onTouchStart={handleMute}
                >
                  Sleep
                </Button>
              )}
            </VStack>{" "}
          </div>
        </Box>
      </Draggable>
    </>
  );
}

export default React.memo(ArtyContainer);
