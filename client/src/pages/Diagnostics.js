import React, { useEffect } from 'react'
import { Grid, Textarea, Box, Text, Table, Tr, Td, Th } from '@chakra-ui/react'
import StreamGraph from '../components/diagnostics/StreamGraph'
import WordCloud from '../components/diagnostics/WordCloud'

function Diagnostics({
    chartMsg
}) {


    useEffect(() => {
        localStorage.getItem(chartMsg)
    }, [chartMsg])
    const downloadFile = async () => {
        let myData = {
          transcript: chartMsg.transcript,
          charts: chartMsg.charts
        }
        const fileName = "file";
        const json = JSON.stringify(myData);
        const blob = new Blob([json], { type: 'application/json' });
        const href = await URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = href;
        link.download = fileName + ".json";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    return (
        <>
            <Grid
                h="full"
                templateRows="repeat(2, 1fr)"
                templateColumns="repeat(2, 1fr)"
                gap={4}
            >
                <Box rowSpan={1} position="relative" colSpan={1} height="50vh" width="50vw">
                    <div>
                        {
                            chartMsg.attributes.length ?
                                <StreamGraph
                                    overHearingData={chartMsg.transcript}
                                    attributes={chartMsg.attributes}
                                    chartMsg={chartMsg}
                                    synonymAttributes={chartMsg.synonymMatrix}
                                    featureAttributes={chartMsg.featureMatrix}
                                />
                                :
                                null
                        }
                    </div>
                </Box>
                <Box rowSpan={1} position="relative" colSpan={1} height="50vh" width="50vw">
                    <div >
                        <WordCloud
                            overHearingData={chartMsg.transcript}
                            attributes={chartMsg.attributes}
                            chartMsg={chartMsg}
                            synonymAttributes={chartMsg.synonymMatrix}
                            featureAttributes={chartMsg.featureMatrix}
                        />
                    </div>
                </Box>
                <Box rowSpan={1} position="relative" colSpan={1} height="50vh" width="50vw">
                    <div style={{ position: "absolute", top: "10%", left: "10%" }}>

                        <Textarea width="40vw" height="40vh" value={chartMsg.transcript} readOnly={true} />
                    </div>
                </Box>
                <Box rowSpan={1} position="relative" colSpan={1} height="50vh" width="50vw">
                    <div style={{ position: "absolute", top: "-20%", left: "10%" }}>

                        <Table>
                            <Tr>
                                <Th>Attribute</Th>
                                <Th>Frequency Count</Th>
                            </Tr>
                            {chartMsg.headerFreq.nominal.map((value, index) => {
                                return (
                                    <>
                                                                <Tr>

                                                                      <Td> {value.header}</Td>
                                        <Td>    {value.count}</Td>
                                        </Tr>

                                    </>
                                )
                            })}
                            {chartMsg.headerFreq.quantitative.map((value, index) => {
                                return (
                                    <>
                                                                <Tr>
                                        <Td> {value.header}</Td>
                                        <Td>    {value.count}</Td>
                                        </Tr>
                                    </>
                                )
                            })}
                        </Table>
                    </div>
                </Box>

            </Grid>
        </>
    )
}

export default Diagnostics