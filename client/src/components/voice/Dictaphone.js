import React, { useState, useEffect } from 'react'
import { Container, Input, Button } from 'semantic-ui-react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'
import "../../style.css"

const Dictaphone = ({
    //   createChartWithVoice,
    setChartMsg,
    createCharts,
    setOverHearingData
}) => {

    const [listening, setListening] = useState(false)
    const [command, setCommand] = useState("")
    const [newTranscript, setNewTranscript] = useState("")
    const [testCommand, setTestCommand] = useState("")

    let commands = [
        {
            command: "*",
            callback: (message) => {
                setCommand(message)
                setChartMsg(prev=>{return {...prev, command: message}})
            }
        }
    ]

    useEffect(() => {
        if (command == "") {
            return
        }

        if (command.includes("show")) {
            createCharts(command)
        }

    }, [command])

    useEffect(() => {
        if (listening) {
            const timer = setTimeout(() => {
                setListening(false)
                console.log('not listening')
            }, 10000)
            return () => {
                clearTimeout(timer)
            }
        }

    }, [listening])

    const { transcript } = useSpeechRecognition({ commands })

    useEffect(() => {
        setChartMsg(prev=>{
            return {...prev, transcript: transcript}
        })
        setOverHearingData(transcript)
    }, [transcript])

    if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
        return null
    } else {
        SpeechRecognition.startListening({ continuous: true })

    }

    return (
        <div className="voiceStyle">
            <Container>
                {/* <p>{transcript}</p> */}
            </Container>
            <Input type="text" onChange={(e)=>setTestCommand(e.target.value)}/>
            <Button onClick={()=>createCharts(testCommand)} color="green">GO</Button>
        </div>
    )
}

export default Dictaphone