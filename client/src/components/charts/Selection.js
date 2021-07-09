import React, { useEffect, useState } from 'react'
import '../../style.css'
import { VegaLite } from 'react-vega'
import {
    Box,
    Grid,
    HStack,
    Accordion,
    AccordionItem,
    AccordionButton,
    AccordionIcon,
    AccordionPanel,
    UnorderedList,
    ListItem,
    Button,
    IconButton,
    VStack
} from "@chakra-ui/react"
import { DeleteIcon } from '@chakra-ui/icons'


function ChartSelection({
    chartMsg,
    chooseChart,
    mute,
    setMute,
    clearCharts
}) {
    // const [charts, setCharts] = useState([])
    // useEffect(() => {
    //     let tmpCharts = []
    //     for(let i = chartMsg.charts.length-1; i >= 0; i--) {
    //         tmpCharts.push(chartMsg.charts[i])
    //     }
    //     setCharts(tmpCharts)
    // }, [chartMsg])
    // console.log(charts)
    return (
        <>

            <Box
                position="absolute"
                bottom="0"
                bg="gray.700"
                width="100vw"
                height="30rem"
                zIndex="1"
                borderTop="2px"
                borderColor="black"
            >
                {/* {
                    mute ?
                        <Button bg='teal.300' mt={2} ml={"1rem"} onClick={() => setMute(false)}>Unmute</Button>
                        :
                        <Button bg='teal.300' mt={2} ml={"1rem"} onClick={() => setMute(true)}>Mute</Button>

                }
                <IconButton colorScheme="red" borderRadius="lg" mt={2} ml={"1rem"} onClick={clearCharts} aria-label="Search database" icon={<DeleteIcon />} /> */}

                <Box zIndex={3} ml={"30rem"} bottom="0" position="absolute"  height="28rem" width="full" overflowY="scroll" overflowX="scroll" >
                    <HStack width="1000rem"  spacing={10} direction="row-reverse" whiteSpace="nowrap">

                        {
                            chartMsg.charts.map((chart, index) => {
                                return (
                                    <>
                                        {
                                            chart ?
                                                <div >
                                                    <ChartPlaceholder
                                                        specification={chart.charts.spec}
                                                        data={chartMsg.data}
                                                        chooseChart={chooseChart}
                                                    />
                                                </div>
                                                :
                                                null
                                        }
                                    </>
                                )
                            })
                        }
                    </HStack>
                </Box>
            </Box>
        </>
    )
}

function ChartPlaceholder({
    specification,
    data,
    chooseChart
}) {
    const [startTime, setStartTime] = useState("")
    const [spec, setSpec] = useState(specification)
    const [hovered, setHovered] = useState(false)
    const [clicked, setClicked] = useState(false)

    specification.x = window.innerWidth / 2
    specification.y = window.innerHeight / 4
    const startTimer = () => {
        setStartTime(performance.now())
        // setSpec(prev => {
        //     return {
        //         ...prev,
        //         width: 700,
        //         height: 500
        //     }
        // })
        setHovered(true)
    }

    const endTimer = () => {
        var timeDiff = performance.now() - startTime
        timeDiff /= 1000;
        specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2))
        // setSpec(prev => {
        //     return {
        //         ...prev,
        //         width: 400,
        //         height: 270
        //     }
        // })
        setHovered(false)
    }


    return (
        <>

            <Box
                bg="transparent"
                // height="28rem"
                zIndex={hovered ? 10 : 3}
                onClick={clicked ? null : () => { endTimer(); chooseChart(specification); setClicked(true) }}
                onMouseOver={startTimer}
                onMouseLeave={endTimer}
                opacity={clicked ? .5 : null}
                bottom="0"

            >
                <Box bg="white" height="100%" width="100%" borderColor="black" borderWidth="3px" rounded="lg" >
                    <VegaLite  height="250" width="300" spec={spec} data={{ table: data }} />
                </Box>
                {/* {
                    hovered ?
                    <HoveredChart
                    spec={spec}
                    data={data}
                    />
                    :
          
                } */}

            </Box>


        </>
    )
}

function HoveredChart({ spec, data }) {
    return (
        <>
            <Box bg="white" borderColor="black" bottom="1" borderWidth="3px" rounded="lg" >
                <VegaLite width={"500px"} height={100} style={{ marginLeft: 10 }} spec={spec} data={{ table: data }} />
            </Box>
        </>
    )
}

export default ChartSelection

