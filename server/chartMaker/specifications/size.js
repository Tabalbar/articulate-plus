module.exports = (chartObj, size) => {
    switch (size) {
        case "small":
            chartObj.charts.spec.width = 100
            chartObj.charts.spec.height = 100
            return chartObj
        case "medium":
            chartObj.charts.spec.width = 200
            chartObj.charts.spec.height = 200
            return chartObj
        case "large":
            chartObj.charts.spec.width = 300
            chartObj.charts.spec.height = 300
            return chartObj
        default:
            chartObj.charts.spec.width = 200
            chartObj.charts.spec.height = 200
            return chartObj

    }
    return chartObj
}