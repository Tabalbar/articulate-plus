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

import attentiveImage from "../../images/attentive.gif";
import idleImage from "../../images/idle.gif";

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
  chartMsg,
  mute,
  setClippyImage,
  startStudy,
  closeChosenCharts,
}) => {
  const [listening, setListening] = useState(false);
  const [command, setCommand] = useState("");

  //commands that the browser will listen to
  let commands = [
    {
      command: "*", // '*' means listen to everything and let useEffect below handle
      callback: (message) => {
        setListening(true); // Currently not used
        setCommand(message); // set state for command to query
        setChartMsg((prev) => {
          return { ...prev, command: message };
        });
      },
    },
  ];

  useEffect(() => {
    if (listening) {
      setClippyImage(attentiveImage);
    } else {
      if (
        !(
          (command.includes("where") ||
            command.includes("see") ||
            command.includes("show") ||
            command.includes("what") ||
            command.includes("make") ||
            ((command.includes("make") ||
              command.includes("modify") ||
              command.includes("pivot") ||
              command.includes("change")) &&
              (command.includes("these") ||
                command.includes("this") ||
                command.includes("those")))) &&
          !mute
        )
      ) {
        setClippyImage(idleImage);
      }
    }
  }, [listening]);

  useEffect(() => {
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
      console.log("fired");
    }
    //Only send command if includes the word "show"
    // & if attrbutes were spoke
    if (
      (command.includes("where") ||
        command.includes("see") ||
        command.includes("show") ||
        command.includes("what") ||
        command.includes("make") ||
        ((command.includes("make") ||
          command.includes("modify") ||
          command.includes("pivot") ||
          command.includes("change")) &&
          (command.includes("these") ||
            command.includes("this") ||
            command.includes("those")))) &&
      !mute
    ) {
      createCharts(command);
    }
    setListening(false);
  }, [command]);

  //Currently not working
  //todo find a way to have browser's voice sythensizer not listen to itself

  // useEffect(() => {
  //   if (!listening) {
  //     const timer = setTimeout(() => {
  //       setListening(true);
  //     }, 5000);
  //     return () => {
  //       clearTimeout(timer);
  //     };
  //   }
  // }, [listening]);

  //Supplay commands commands
  const { transcript } = useSpeechRecognition({ commands });

  //Check if able to use browser's speech recognition
  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return null;
  } else {
    if (startStudy) {
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
