module.exports = (chartObj, actualCommand) => {
    chartObj.charts.spec.title = actualCommand
    return chartObj
}