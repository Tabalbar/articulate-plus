module.exports = (chartObj, intent, extractedHeaders) => {
    let layerMark = "";
    if (extractedHeaders.length > 3) {

        switch (intent) {
            case "bar":
                delete chartObj.charts.spec.mark
                layerMark = "bar"
                return chartObj, layerMark;
            case "line":
                delete chartObj.charts.spec.mark
                layerMark = "line"
                return chartObj, layerMark
            case "scatter":
                delete chartObj.charts.spec.mark
                layerMark = "point"
                return chartObj, layerMark
            case "pie":
                delete chartObj.charts.spec.mark
                layerMark = "arc"
                return chartObj, layerMark
            case "marginalHistogram":
                delete chartObj.charts.spec.mark
                return chartObj
            case "heatmap":
                delete chartObj.charts.spec.mark
                layerMark = "rect"
                return chartObj, layerMark
            case "lineArea":
                layerMark = "area"
                return chartObj, layerMark
            case "stackedBar":
                layerMark = "bar"
                return chartObj, layerMark
            case "normalizedStackedBar":
                layerMark = "bar"
                return chartObj, layerMark
            case "normalizedLineArea":
                layerMark = "area"

                return chartObj, layerMark
            // case "candleStick":
            //     chartObj.charts.spec.mark = "bar"
            //     return chartObj
            case "parallelCoordinates":
                chartObj.charts.spec.mark = "line"
                return chartObj


        }
    }

    switch (intent) {
        case "bar":
            chartObj.charts.spec.mark = "bar"
            return chartObj;
        case "lineArea":
            chartObj.charts.spec.mark = "area"
            return chartObj
        case "line":
            chartObj.charts.spec.mark = "line"
            return chartObj
        case "scatter":
            chartObj.charts.spec.mark = "point"
            return chartObj
        case "pie":
            chartObj.charts.spec.mark = "arc"
            return chartObj
        case "marginalHistogram":

            delete chartObj.charts.spec.mark
            return chartObj
        case "heatmap":
            chartObj.charts.spec.mark = "rect"
            return chartObj
        case "stackedBar":
            chartObj.charts.spec.mark = { type: "bar", cornerRadiusTopLeft: 3, cornerRadiusTopRight: 3 }
            return chartObj
        case "normalizedStackedBar":
            chartObj.charts.spec.mark = "bar"
            return chartObj
        case "normalizedLineArea":
            chartObj.charts.spec.mark = "area"
            return chartObj
        // case "candleStick":
        //     chartObj.charts.spec.mark = "bar"
        //     return chartObj
        case "parallelCoordinates":
            chartObj.charts.spec.mark = "line"
            return chartObj


    }
    return chartObj
}