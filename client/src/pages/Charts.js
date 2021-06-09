import React, { useEffect, useState } from 'react'
import ChartSelection from '../components/charts/ChartSelection'
import ChosenCharts from '../components/charts/ChosenCharts'
import FileInput from '../components/charts/FileInput'

function Charts({
    setOverHearingData,
    overHearingData,
    chartMsg, 
    setChartMsg,
    charts,
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
            />
        </>
    )
}

export default Charts