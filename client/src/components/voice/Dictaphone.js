import React, { useState, useEffect } from "react";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import "../../style.css";
import { Box, Center } from "@chakra-ui/react";

const Dictaphone = ({ setChartMsg, createCharts, chartMsg }) => {
  const [listening, setListening] = useState(true);
  const [command, setCommand] = useState("");

  let commands = [
    {
      command: "*",
      callback: (message) => {
        setListening(false);
        setCommand(message);
        setChartMsg((prev) => {
          return { ...prev, command: message };
        });
      },
    },
  ];

  useEffect(() => {
    if (command === "") {
      return;
    }
    setChartMsg((prev) => {
      return { ...prev, transcript: prev.transcript + ". " + command };
    });
    if (
      command.includes("show") &&
      checkForAttributes(command, chartMsg.synonymMatrix)
    ) {
      createCharts(command);
    }
  }, [command]);

  useEffect(() => {
    if (!listening) {
      const timer = setTimeout(() => {
        setListening(true);
      }, 2000);
      return () => {
        clearTimeout(timer);
      };
    }
  }, [listening]);

  const { transcript } = useSpeechRecognition({ commands });

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
