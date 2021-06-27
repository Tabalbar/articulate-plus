import React, { useEffect, useState } from 'react'
import '../../style.css'
import { VegaLite } from 'react-vega'
import Attributes from '../TreeMenu'
import { Box, Grid, HStack, Tooltip, Text } from "@chakra-ui/react"


function ChartSelection({
    chartMsg,
    chooseChart
}) {

    useEffect(() => {

    }, [])
    const numAttributes = chartMsg.attributes.length
    return (
        <>

            <Box bg="gray.800"
                position="absolute"
                bottom="0"
                width="100vw"
                height="33rem"
                zIndex="1"
                borderTop="2px"
                borderColor="black"
            >
                <Box position="relative"  borderColor="black"
                    borderBottom="2px" bg="white" overflow="hidden"  height="4rem">
                    <Grid templateColumns={`repeat(${numAttributes}, 1fr)`} gap={1}>
                        {chartMsg.attributes.map((value, index) => {
                            return (
                                <Tooltip placement="top" label="Insert filter Attributes Here" aria-label="A tooltip">

                                    <Text fontSize="xl">
                                        {value}
                                    </Text>
                                </Tooltip>
                            )
                        })}
                    </Grid>
                </Box>
                

            </Box>
            <Box position="fixed" zIndex={3} bottom="5" height="26rem"  overflowX="scroll" >
                    <HStack spacing="5rem" width="100vw" >
                        {
                            chartMsg.charts.slice(0).reverse().map((chart, index) => {
                                return (
                                    <>
                                        {
                                            chart ?
                                                    <ChartPlaceholder
                                                        specification={chart.charts.spec}
                                                        data={chartMsg.data}
                                                        chooseChart={chooseChart}
                                                    />
                                                :
                                                null
                                        }
                                    </>
                                )
                            })
                        }
                    </HStack>
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
        setSpec(prev => {
            return {
                ...prev,
                width: "800",
                height: 600
            }
        })
        setHovered(true)
    }

    const endTimer = () => {
        var timeDiff = performance.now() - startTime
        timeDiff /= 1000;
        specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2))
        setSpec(prev => {
            return {
                ...prev,
                width: 400,
                height: 270
            }
        })
        setHovered(false)
    }


    return (
        <>
 
            <Box
                bg="transparent"
                // height="25vh"
                zIndex="3"
                onClick={() => { endTimer(); chooseChart(specification); setClicked(true) }}
                onMouseOver={startTimer}
                onMouseLeave={endTimer}
                position="relative"
                bottom="0"
                display={clicked ? "None" : null}
                m={1}
            >
                <Box bg="white" width={hovered ? "65rem" : null}  zIndex={hovered ? "10" : null} borderColor="black" bottom="1" borderWidth="3px" rounded="lg" >
                    <VegaLite style={{ marginLeft: 10 }} spec={spec} data={{ table: data }} />
                </Box>
            </Box>


        </>
    )
}

export default ChartSelection

