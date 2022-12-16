/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
import React, { useState } from "react";
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
  const eventLogger = (e, data) => {};

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
        onStop={eventLogger}
      >
        <Box position="absolute" zIndex={999999} className="react-draggable">
          <div
            className="handle"
            style={{
              cursor: "move",
            }}
          >
            <VStack>
              <Tooltip
                label={voiceMsg}
                fontSize="3xl"
                position="relative"
                placement="left-start"
                isOpen={showTooltip}
                hasArrow
              >
                <Box>
                  <Image
                    ml={"3rem"}
                    boxSize="10rem"
                    className="handle"
                    src={clippyImage}
                    fallback={<Box ml={"3rem"} boxSize="10rem" />}
                    draggable="false"
                    userSelect="none"
                  />
                </Box>
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
