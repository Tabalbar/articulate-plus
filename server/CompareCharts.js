module.exports = (chartMsg) => {
    for(let i = 0; i < chartMsg.charts.length; i++) {
        if(isChartsEqual(chartMsg.explicitChart, chartMsg.charts[i])) {
            chartMsg.explicitChart = ""
            break;
        }
    }
    for(let i = 0; i < chartMsg.charts.length; i++) {
        if(isChartsEqual(chartMsg.inferredChart, chartMsg.charts[i])) {
            chartMsg.inferredChart = ""
            break
        }
    }
    for(let i = 0; i < chartMsg.charts.length; i++) {
        if(isChartsEqual(chartMsg.modifiedChart, chartMsg.charts[i])) {
            chartMsg.modifiedChart = ""
            break
        }
    }

    if (isChartsEqual(chartMsg.explicitChart, chartMsg.inferredChart) && isChartsEqual(chartMsg.explicitChart, chartMsg.modifiedChart) && chartMsg.explicitChart !== "") {
        chartMsg.inferredChart = ""
        chartMsg.modifiedChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Window and Modifed"
    } else if(isChartsEqual(chartMsg.explicitChart, chartMsg.inferredChart) && chartMsg.explicitChart !== "") {
        chartMsg.inferredChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Window"
    } else if(isChartsEqual(chartMsg.explicitChart, chartMsg.modifiedChart) && chartMsg.explicitChart !== "") {
        chartMsg.inferredChart = ""
        chartMsg.explicitChart.charts.spec.chartSelection = "Explicit and Modified"
    } else if(isChartsEqual(chartMsg.inferredChart, chartMsg.modifiedChart) && chartMsg.inferredChart !== "") {
        chartMsg.modifiedChart = ""
        chartMsg.inferredChart.charts.spec.chartSelection = "Window and Modified"
    }
    
}

function isChartsEqual(chartOne, chartTwo) {
    if(chartOne == "" && chartTwo == "") {
        return true
    }
    if(chartOne == "" && chartTwo !== "") {
        return false
    }
    if(chartOne !== "" && chartTwo == "") {
        return false
    }
    chartOne = chartOne.charts.spec
    chartTwo = chartTwo.charts.spec

    if(JSON.stringify(chartOne.encoding) == JSON.stringify(chartTwo.encoding)
    && JSON.stringify(chartOne.mark) == JSON.stringify(chartTwo.mark)
    && JSON.stringify(chartOne.transform) == JSON.stringify(chartTwo.transform)) {
        return true
    } else {
        return false
    }
}

