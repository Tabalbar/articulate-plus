import React, { useState, useEffect } from 'react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'
import "../../style.css"
import talking from '../../images/talking.gif'
import notTalking from '../../images/notTalking.png'
import { Box, Image, Center, Input, Button } from "@chakra-ui/react"
import Siriwave from 'react-siriwave';
import Audio from './Audio'

const Dictaphone = ({
    //   createChartWithVoice,
    setChartMsg,
    createCharts,
    setOverHearingData,
    chartMsg
}) => {

    const [listening, setListening] = useState(false)
    const [command, setCommand] = useState("")
    const [testCommand, setTestCommand] = useState("")

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

        if (command.includes("show")) {
            createCharts(command)
        }
        setChartMsg(prev => {
            return { ...prev, transcript: prev.transcript + ". " + command }
        })
    }, [command])

    useEffect(() => {
        if (listening) {
            const timer = setTimeout(() => {
                setListening(false)
                console.log('not listening')
            }, 2000)
            return () => {
                clearTimeout(timer)
            }
        }

    }, [listening])

    const { transcript } = useSpeechRecognition({ commands })

    // useEffect(() => {
    //     console.log(chartMsg.transcript)
    // }, [transcript])


    useEffect(() => {
        // setChartMsg(prev=>{
        //     return{}
        // })

        setOverHearingData(transcript)
    }, [transcript])

    if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
        return null
    } else {
        SpeechRecognition.startListening({ continuous: true })

    }



    // .voiceStyle {
    //     background-color: rgb(0, 37, 40);
    //     overflow: hidden;
    //     position: fixed;
    //     bottom: 0;
    //     width: 100%;
    //     height: 50px;
    //     z-index: 1;
    //     border-top:#C24C3D solid; 
    // }
    return (
        <>
        <Center>

            <Box
                top="0"
                overflow="hidden"
                zIndex="2"
                position="sticky"
                bg="black"
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

export default Dictaphone