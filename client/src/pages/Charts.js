import React from 'react'
import ChartSelection from '../components/charts/Selection'
import ChosenCharts from '../components/charts/Chosen'
import FileInput from '../components/charts/FileInput'

function Charts({
    chartMsg, 
    setChartMsg,
    charts,
    setCharts,
    chooseChart
}) {



    return (
        <>
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