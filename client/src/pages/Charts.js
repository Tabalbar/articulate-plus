import React, { useEffect, useState } from 'react'
import ChartSelection from '../components/charts/Selection'
import ChosenCharts from '../components/charts/Chosen'
import FileInput from '../components/charts/FileInput'

function Charts({
    setOverHearingData,
    overHearingData,
    chartMsg, 
    setChartMsg,
    charts,
    setCharts,
    chooseChart
}) {



    return (
        <>
            <FileInput 
                setChartMsg={setChartMsg}
            />
            <ChartSelection
                chartMsg={chartMsg}
                chooseChart={chooseChart}
            />
            <ChosenCharts
                chartMsg={chartMsg}
                charts={charts}
                setCharts={setCharts}
            />
        </>
    )
}

export default Charts