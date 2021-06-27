import React, { useState, useEffect } from 'react'
import { VegaLite } from 'react-vega'
import nlp from 'compromise'

const StreamGraph = ({
    overHearingData,
    attributes,
    synonymAttributes,
    featureAttributes
}) => {

    const [streamData, setStreamData] = useState([])
    const [nounsLength, setNounsLength] = useState(0)
    
    const specification = {
        width: 150,
        height: 150,
        mark: "area",
        encoding: {
            x: {
                // timeUnit: "seconds",
                field: "date",
                axis: null
            },
            y: {
                aggregate: "sum",
                field: "count",
                // axis: null,
                stack: "center"
            },
            color: { field: "header" }
        },
        data: { name: 'table' }
    }

    useEffect(() => {
        let tmpStreamData = []
        for (let i = 0; i < attributes.length; i++) {
            tmpStreamData.push({ header: attributes[i], count: 0, date: new Date() })
        }
        setStreamData(tmpStreamData)
    }, [attributes])

    useEffect(() => {
        let doc = nlp(overHearingData)
        let nouns = doc.nouns().out('array')
        setNounsLength(nouns.length)

        let tmpStreamData = streamData
        if (nouns.length > nounsLength) {
            let lastTerm = nouns[nouns.length - 1]
            for (let i = 0; i < synonymAttributes.length; i++) {
                for (let j = 0; j < synonymAttributes[i].length; j++) {
                    if (lastTerm.toLowerCase() === synonymAttributes[i][j].toLowerCase()) {
                        tmpStreamData.push({
                            header: synonymAttributes[i][0],
                            count: 1,
                            date: new Date()
                        })
                    }
                }
            }
            for (let i = 0; i < featureAttributes.length; i++) {
                for (let j = 0; j < featureAttributes[i].length; j++) {
                    if (lastTerm.toLowerCase() === featureAttributes[i][j].toLowerCase()) {
                        tmpStreamData.push({
                            header: featureAttributes[i][0],
                            count: 1,
                            date: new Date()
                        })

                    }
                }
            }
        }
        setStreamData(tmpStreamData.flat())
    }, [overHearingData])
    return (
        <>
            <VegaLite spec={specification} data={{ table: streamData }} />
        </>
    )
}

export default StreamGraph