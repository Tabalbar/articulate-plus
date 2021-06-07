const findType = require("../findType")
const findMissing = require("../findMissing").findMissing

module.exports = (chartObj, extractedHeaders, data, headerFreq, command) => {
    if(extractedHeaders.length < 2) {
        extractedHeaders =  findMissing(extractedHeaders, data, 2, headerFreq, command, "QQQ")
    }
    chartObj.charts.spec.vconcat = [
        {
            mark: "bar",
            height: 60,
            encoding: {
                x: { bin: true, field: extractedHeaders[0], axis: null },
                y: { aggregate: "count", scale: { domain: [0, 500] }, title: "" }
            }
        },
        {
            spacing: 15,
            bounds: "flush",
            hconcat: [
                {
                    mark: "rect",
                    encoding: {
                        x: { bin: true, field: extractedHeaders[0], type: "quantitative" },
                        y: { bin: true, field: extractedHeaders[1], type: "quantitative" },
                        color: { aggregate: "count" }
                    }
                },
                {
                    mark: "bar",
                    width: 60,
                    encoding: {
                        y: { "bin": true, field: extractedHeaders[1], axis: null },
                        x: {
                            aggregate: "count",
                            scale: { domain: [0, 500] },
                            title: ""
                        }
                    }
                }
            ]
        }
    ]
    return chartObj
}