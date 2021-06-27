module.exports = (chartMsg) => {
    for(let i = 0; i < chartMsg.charts; i++) {
        if(JSON.stringify(chartMsg.explicitChart.charts) == JSON.stringify(chartMsg.charts[i].charts)) {
            chartMsg.explicitChart = ""
        }
        if(JSON.stringify(chartMsg.inferredChart).charts == JSON.stringify(chartMsg.charts[i].charts)) {
            chartMsg.inferredChart = ""
        }
        if(JSON.stringify(chartMsg.modifiedChart).charts == JSON.stringify(chartMsg.charts[i].charts)) {
            chartMsg.modifiedChart = ""
        }
    }
    if (JSON.stringify(chartMsg.explicitChart) == JSON.stringify(chartMsg.inferredChart) && JSON.stringify(chartMsg.explicitChart) == JSON.stringify(chartMsg.modifiedChart)) {
        chartMsg.inferredChart = ""
        chartMsg.modifiedChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Window and Modifed"
    } else if(JSON.stringify(chartMsg.explicitChart) == JSON.stringify(chartMsg.inferredChart)) {
        chartMsg.inferredChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Window"
    } else if(JSON.stringify(chartMsg.explicitChart) == JSON.stringify(chartMsg.modifiedChart)) {
        chartMsg.inferredChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Modified"
    } else if(JSON.stringify(chartMsg.inferredChart) == JSON.stringify(chartMsg.modifiedChart)) {
        chartMsg.modifiedChart = ""
        chartMsg.inferredChart.charts.spec.chartSelection = "Window and Modified"
    }

    
}

