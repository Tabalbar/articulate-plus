import React from 'react'
import ChartSelection from '../components/charts/Selection'
import ChosenCharts from '../components/charts/Chosen'

function Charts({
    chartMsg, 
    setChartMsg,
    charts,
    setCharts,
    chooseChart,
    mute,
    setMute,
    clearCharts
}) {


    return (
        <>
            <ChartSelection
                chartMsg={chartMsg}
                chooseChart={chooseChart}
                mute={mute}
                setMute={setMute}
                clearCharts={clearCharts}
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