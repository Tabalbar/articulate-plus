import React, { useState, useEffect } from "react";

//browser speech recognition
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

//styles
import "../../style.css";

//chakra ui imports
import { Box, Center } from "@chakra-ui/react";

//helper function
import createDate from "../../helpers/createDate";

import attentiveImage from "../../images/attentive-small.gif";
import useInterval from "../../helpers/useInterval";

/**
 * Uses react-speech-recognition API that uses the browser to translate
 * spoken language into text
 *
 * @param {function} setChartMsg callback to set the state of chartMsg
 * @param {function} createCharts API call to server to request charts
 * @param {object} chartMsg state of the chartMsg for API call
 * @returns
 */
const Dictaphone = ({
  setChartMsg,
  createCharts,
  mute,
  setClippyImage,
  startStudy,
  closeChosenCharts,
  modifiedChartOptions,
}) => {
  const [listening, setListening] = useState(true);
  const [command, setCommand] = useState("");

  //commands that the browser will listen to
  let commands = [
    {
      command: "*", // '*' means listen to everything and let useEffect below handle
      callback: (message) => {
        setClippyImage(attentiveImage);
        setCommand(message.toLowerCase()); // set state for command to query
        setChartMsg((prev) => {
          return { ...prev, command: message };
        });
      },
    },
  ];

  useEffect(async () => {
    //Check if words were actually spoken
    if (command === "") {
      return;
    }

    //Set state for message to send to node service
    if (!mute) {
      setChartMsg((prev) => {
        if (prev.transcript !== "") {
          return {
            ...prev,
            transcript: prev.transcript + ". " + command,
            loggedTranscript: [
              ...prev.loggedTranscript,
              { sentence: command, date: createDate() },
            ],
          };
        } else {
          return {
            ...prev,
            transcript: prev.transcript + "" + command,
            loggedTranscript: [
              ...prev.loggedTranscript,
              { sentence: command, date: createDate() },
            ],
          };
        }
      });
    } else {
      setChartMsg((prev) => {
        return {
          ...prev,
          uncontrolledTranscript: prev.uncontrolledTranscript + ". " + command,
          loggedUncontrolledTranscript: [
            ...prev.loggedUncontrolledTranscript,
            { sentence: command, date: createDate() },
          ],
        };
      });
    }
    if (command.includes("delete all chosen charts")) {
      closeChosenCharts();
    }

    const isCommand = await createCharts(command);
    if (isCommand) {
      setListening(false);
      setTimeout(() => {
        setListening(true);
      }, 8000);
    }
  }, [command]);

  //Create charts at a random interval
  useInterval(() => {
    if (modifiedChartOptions.randomCharts.toggle && startStudy) {
      setListening(false);
      createCharts("random");
      setTimeout(() => {
        setListening(true);
      }, 8000);
    }
  }, modifiedChartOptions.randomCharts.minutes * 60 * 1000);

  //Supply commands
  const { transcript } = useSpeechRecognition({ commands });

  //Check if able to use browser's speech recognition
  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return null;
  } else {
    if (startStudy && listening) {
      SpeechRecognition.startListening({ continuous: true });
    }
  }

  return (
    <>
      <Center>
        <Box
          top="0"
          overflow="hidden"
          zIndex="2"
          position="absolute"
          bg="white"
        ></Box>
      </Center>
    </>
  );
};

//Helper to check if any attibutes were spoken in the command
function checkForAttributes(command, attributes) {
  for (let i = 0; i < attributes.length; i++) {
    for (let j = 0; j < attributes[i].length; j++) {
      if (command.includes(attributes[i][j])) {
        return true;
      }
    }
  }
  return false;
}

export default Dictaphone;
