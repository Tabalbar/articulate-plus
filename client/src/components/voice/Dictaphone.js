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
import ChartObj from "../../shared/ChartObj";

/**
 * Uses react-speech-recognition API that uses the browser to translate
 * spoken language into text
 *
 * @param {function} setChartMsg callback to set the state of chartMsg
 * @param {object} chartMsg state of the chartMsg for API call
 * @returns
 */
const Dictaphone = ({ setChartMsg, mute }) => {
  const [command, setCommand] = useState("");

  //commands that the browser will listen to
  let commands = [
    {
      command: "*", // '*' means listen to everything and let useEffect below handle
      callback: (message) => {
        setCommand(message); // set state for command to query
      },
    },
  ];

  useEffect(() => {
    //Check if words were actually spoken
    if (command === "") {
      return;
    }

    //Set state for message to send to node service
    if (!mute) {
      ChartObj.addToTranscripts(command, mute);
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

    //Only send command if includes the word "show"
    // & if attrbutes were spoke
    if (
      (command.includes("where") ||
        command.includes("see") ||
        command.includes("show")) &&
      !mute
    ) {
      ChartObj.serverRequest(command);
    }
  }, [command]);

  const { transcript } = useSpeechRecognition({ commands });

  //Check if able to use browser's speech recognition
  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return null;
  } else {
    SpeechRecognition.startListening({ continuous: true });
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
