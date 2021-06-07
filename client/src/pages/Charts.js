import React, { useEffect, useState } from 'react'
import ChartSelection from '../components/charts/ChartSelection'
import ChosenCharts from '../components/charts/ChosenCharts'
import FileInput from '../components/charts/FileInput'

function Charts({
    setOverHearingData,
    overHearingData,
    chartMsg, 
    setChartMsg
}) {




    return (
        <>
            <FileInput 
                setChartMsg={setChartMsg}
            />
            <ChartSelection

            />
            <ChosenCharts

            />
        </>
    )
}

export default Charts