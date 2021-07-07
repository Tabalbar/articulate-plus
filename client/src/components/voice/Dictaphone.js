import React, { useState, useEffect } from 'react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'
import "../../style.css"
import { Box, Center } from "@chakra-ui/react"
import Audio from './Audio'
import {transcriptState} from '../../shared/overHearing'
import {useRecoilState} from 'recoil'
import nlp from 'compromise'

const Dictaphone = ({
    //   createChartWithVoice,
    setChartMsg,
    createCharts,
    chartMsg
}) => {

    const [listening, setListening] = useState(false)
    const [command, setCommand] = useState("")
    const [text, setText] = useRecoilState(transcriptState)

    let commands = [
        {
            command: "*",
            callback: (message) => {
                setListening(true)
                setCommand(message)
                setChartMsg(prev => { return { ...prev, command: message } })
            }
        }
    ]

    useEffect(() => {
        if (command === "") {
            return
        }
        setText((prev)=>prev+ " " + command)
        setChartMsg(prev => {
            return { ...prev, transcript: prev.transcript + ". " + command }
        })
        if (command.includes("show") && checkForAttributes(command, chartMsg.synonymMatrix)) {
            createCharts(command)
        }

    }, [command])

    useEffect(() => {
        if (listening) {
            const timer = setTimeout(() => {
                setListening(false)
            }, 2000)
            return () => {
                clearTimeout(timer)
            }
        }

    }, [listening])

    const { transcript } = useSpeechRecognition({ commands })


    useEffect(() => {
        // setOverHearingData(transcript)
    }, [transcript])

    if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
        return null
    } else {
        SpeechRecognition.startListening({ continuous: true })

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
                // width="10vw"
                // border="black"
                // borderRadius="lg"
            >   
                    {/* <Siriwave curveDefinition={<Audio/>} style="ios9" amplitude={listening ? 5 : 0} /> */}
                    <Audio/>
                {/* <Image   marginLeft="auto" height="full" marginRight="auto" width="5vw" position="relative" src={listening ? talking : notTalking}></Image> */}

            </Box>
            </Center>
            {/* <Box
                bg="teal.800"
                bottom="0"
                overflow="hidden"
                width="100vw"
                height="50px"
                zIndex="1"
                position="fixed"
                borderTop="#C24C3D solid"
                p={1}
            >



                <Input width="40rem" zIndex="5" bg="white" type="text" onChange={(e) => setTestCommand(e.target.value)} />
                <Button ml={1} variant="outline" onClick={() => createCharts(testCommand)} bg="teal.300">GO</Button>

            </Box> */}
        </>
    )
}

function checkForAttributes(command, attributes) {
    
    for(let i = 0; i < attributes.length; i++ ) {
        for(let j = 0; j < attributes[i].length; j++) {
            if(command.includes(attributes[i][j])){
                return true
            }
        }
    }
    return false
}

export default Dictaphone