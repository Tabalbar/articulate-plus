const findMissing = require("../findMissing").findMissing
const findType = require("../findType")

module.exports = (chartObj, extractedHeaders, data, headerFreq, command) => {

    // for(let i = 0; i < extractedHeaders.length; i++) {
    //     let chart = chartObj.charts
    //     if(findType(extractedHeaders[i], data) == "nominal") {
    //         chart.spec.mark = "bar";
    //         chart.spec.encoding.x = {
    //             field: extractedHeaders[i],
    //             type: findType(extractedHeaders[i], data)
    //         }
    //         chart.spec.encoding.y = {
    //             aggregate: 'count'
    //         }
    //     }
    //     chartObj.extraCharts.push({chart: chart, message: ("I can't make a heatmap with nominal data, but here is a distribution of", extractedHeaders[i])})
    //     extractedHeaders.splice(i, 1);
    // }
    let numHeaders = extractedHeaders.length
    if (numHeaders > 3) {
        numHeaders = 4
    }

    switch (numHeaders) {
        case 1:
        extractedHeaders =  findMissing(extractedHeaders, data, 2, headerFreq, command, "QQQ")
        case 2:
            for(let i = 0; i < extractedHeaders.length; i++) {
                if(findType(extractedHeaders[i], data) == "nominal") {
                    extractedHeaders.splice(i,1)
                }
                extractedHeaders = findMissing(extractedHeaders, data, 2, headerFreq, command, "QQQ")
            }

            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                bin: true,
                type: findType(extractedHeaders[0], data)
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                bin: true,
                type: findType(extractedHeaders[1], data)
            }
            chartObj.charts.spec.encoding.color = { aggregate: "count", type: "quantitative" }
            return chartObj


        case 3:
            chartObj.charts.spec.encoding.columns = {
                field: extractedHeaders[2],
                bin: true,
                type: findType(extractedHeaders[2], data)
            }
            chartObj.charts.spec.encoding.x = {
                field: extractedHeaders[0],
                bin: true,
                type: findType(extractedHeaders[0], data)
            }
            chartObj.charts.spec.encoding.y = {
                field: extractedHeaders[1],
                bin: true,
                type: findType(extractedHeaders[1], data)
            }
            chartObj.charts.spec.encoding.color = { aggregate: "count", type: "quantitative" }
            return chartObj
        case 4:
            chartObj.charts.spec.columns = extractedHeaders.length - 1
            chartObj.charts.spec.concat = createLayers(extractedHeaders, data)
            delete chartObj.charts.spec.encoding
            return chartObj
        default:
            chartObj.errMsg = "Error"
            return chartObj
    }
}

function createLayers(extractedHeaders, data) {
    let layers = [];
    for (let i = 1; i < extractedHeaders.length; i++) {
        if (layerMark === "rect") {
            layers.push({
                layer: [
                    {
                        mark: layerMark,
                        encoding: {
                            x: { field: extractedHeaders[i], type: findType(extractedHeaders[i], data), bin: true },
                            y: { field: extractedHeaders[0], type: findType(extractedHeaders[0], data), bin: true },
                            color: { aggregate: "count", type: "quantitative" }

                        }
                    }
                ]
            })
        }
    }
    return layers
}