const findType = require("../findType")
const pearsonCorrelation = require('../helperFunctions/pearsonCorrelation')
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, extractedHeaders, data, headerFreq, command) => {
    let folds = reorderForParallel(extractedHeaders, data)
    chartObj.charts.spec.encoding.color = { type: "nominal", field: extractedHeaders[0] }
    chartObj.charts.spec.encoding.detail = { type: "nominal", field: "index" }
    chartObj.charts.spec.encoding.opacity = { value: 0.3 }
    chartObj.charts.spec.encoding.x = { type: "nominal", field: "key" }
    chartObj.charts.spec.encoding.y = { type: "quantitative", field: "value" }

    chartObj.charts.spec.transform = [
        { window: [{ op: "count", as: "index" }] },
        { fold: folds }
    ]

    return chartObj
}

function reorderForParallel(extractedHeaders, data) {
    let folds = []
    for (let i = 0; i < extractedHeaders.length; i++) {
        if (findType(extractedHeaders[i], data) === "nominal") {
            let tmpHeader = extractedHeaders[0]
            extractedHeaders[0] = extractedHeaders[i]
            extractedHeaders[i] = tmpHeader
        }
    }
    folds.push(extractedHeaders[1])
    let series = []
    for(let i = 1; i < extractedHeaders.length; i++) {
        let tmp = []
        for(let j = 0; j < data.length; j++) {
            tmp.push(data[j][extractedHeaders[i]])
        }
        series.push(tmp)
    }

    for(let i = 1; i < series.length; i++) {
        for(let j = i+1; j< series.length; j++) {
            if(pearsonCorrelation(series[i], series[j]) < pearsonCorrelation(series[i], series[j])) {
                let tmpSeries = series[j]
                series[i] = series[j]
                series[j] = tmpSeries
                let tmpHeader = extractedHeaders[j]
                extractedHeaders[i+1] = extractedHeaders[j]
                extractedHeaders[j] = tmpHeader
            }
        }
        // if(i == series.length-1) {
 
        //     folds.push(extractedHeaders[i])
        //     break
        // }
        
    }
    for(let i = 1; i < extractedHeaders.length; i++) {
        folds.push(extractedHeaders[i])
    }
    
    return folds.flat();
}