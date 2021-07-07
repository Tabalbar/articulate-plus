import React, {useState} from 'react'
import {
    Drawer,
    DrawerBody,
    DrawerFooter,
    DrawerHeader,
    DrawerOverlay,
    DrawerContent,
    DrawerCloseButton,
    Button,
    Text,
    useDisclosure,
    Box,
    IconButton,
    Stack,
    Radio,
    Input,
    Textarea
} from "@chakra-ui/react"
import { ArrowRightIcon } from '@chakra-ui/icons'
import FileInput from './FileInput'
import {useRecoilState} from 'recoil'
import {transcriptState} from '../../shared/overHearing'
 
function SideMenu({ setChartMsg, modifiedChartOptions, setModifiedChartOptions }) {

    const { isOpen, onOpen, onClose } = useDisclosure()
    const [transcriptText, setTranscriptText] = useRecoilState(transcriptState)
    const [text, setText] = useState("")

    const btnRef = React.useRef()
    const handleWindowPastSenteces = (e) => {
        e.preventDefault();
        let pastSentences = e.target.value
        // if(!isNaN(pastSentences)) {
        //     pastSentences = 0
        // }
        setModifiedChartOptions(prev => {
            return {
                ...prev,
                window: {
                    toggle: true,
                    pastSentences: parseInt(pastSentences)
                }
            }
        })
    }

    return (
        <>
            <Box position="absolute" left="0" top="50%" zIndex="10">
                <IconButton variant="outline" colorScheme="teal" size="lg" aria-label="Search database" onClick={onOpen} icon={<ArrowRightIcon />} />
            </Box>
            <Drawer
                isOpen={isOpen}
                placement="left"
                onClose={onClose}
                finalFocusRef={btnRef}
            >
                <DrawerOverlay />
                <DrawerContent>
                    <DrawerCloseButton borderColor="red" border="1px" color="red" variant="outline" />
                    <DrawerHeader>Admin</DrawerHeader>

                    <DrawerBody>
                        <Text fontWeight="bold" ml={1}>Load Dataset</Text>
                        <FileInput
                            setChartMsg={setChartMsg}
                        />
                        <br />
                        <br />
                        <br />
                        <br />
                        <Text fontWeight="bold" ml={1}>Modified Chart Options</Text>
                        <Stack>
                            <Radio isChecked={modifiedChartOptions.window.toggle}
                                onClick={() => setModifiedChartOptions(prev => { return { ...prev, window: { toggle: !prev.window.toggle, pastSentences: prev.window.pastSentences } } })}
                                size="lg" colorScheme="teal">
                                Sentence Window
                            </Radio>
                            {
                                modifiedChartOptions.window.toggle ?
                                    <Input type="number" value={modifiedChartOptions.window.pastSentences} onChange={handleWindowPastSenteces} />
                                    :
                                    null
                            }
                            {
                                modifiedChartOptions.window.toggle ?
                                    <Radio isChecked={modifiedChartOptions.semanticAnalysis}
                                        onClick={() => setModifiedChartOptions(prev => { return { ...prev, semanticAnalysis: !prev.semanticAnalysis } })}
                                        size="lg" colorScheme="teal">
                                        Sentiment Analysis
                                    </Radio>
                                    :
                                    null
                            }

                            <Radio isChecked={modifiedChartOptions.neuralNetwork}
                                onClick={() => setModifiedChartOptions(prev => { return { ...prev, neuralNetwork: !prev.neuralNetwork } })}
                                size="lg" colorScheme="teal">
                                Neural Network (NodeNLP)
                            </Radio>

                        </Stack>

                        {/**-----------------USED FOR DEBUGGING TRANSCIPRTION------------ */}
                        {/* <Textarea value={text} onChange={(e)=>setText(e.target.value)}></Textarea>
                        <Textarea value={transcriptText}></Textarea>
                        <Button onClick={()=>setTranscriptText(text)}></Button> */}
                    </DrawerBody>

                    <DrawerFooter>
                        <Button variant="outline" mr={3} onClick={onClose}>
                            Cancel
                        </Button>
                        <Button colorScheme="blue">Save</Button>
                    </DrawerFooter>
                </DrawerContent>
            </Drawer>
        </>
    )
}

export default SideMenu