import React, { useEffect } from 'react'
import { Grid, Placeholder } from 'semantic-ui-react'
import '../../style.css'
import { VegaLite } from 'react-vega'

function ChartSelection({
    chartMsg,
    chooseChart
}) {

    return (
        <>
            <div className="ChartSelection">
                <Grid centered={true}>
                    <Grid.Column>
                        <Grid.Row>
                            {
                                chartMsg.explicitChart ?
                                    <ChartPlaceholder
                                        chartSelection={true}
                                        specification={chartMsg.explicitChart.charts.spec}
                                        data={chartMsg.data}
                                        chooseChart={chooseChart}
                                    />
                                    :
                                    null
                            }

                        </Grid.Row>
                        <Grid.Row>
                            {
                                chartMsg.explicitChart ?
                                    <ChartPlaceholder
                                        chartSelection={true}
                                        specification={chartMsg.explicitChart.charts.spec}
                                        data={chartMsg.data}
                                        chooseChart={chooseChart}
                                    />
                                    :
                                    null
                            }
                        </Grid.Row>
                        <Grid.Row>
                            {
                                chartMsg.explicitChart ?
                                    <ChartPlaceholder
                                        chartSelection={true}
                                        specification={chartMsg.explicitChart.charts.spec}
                                        data={chartMsg.data}
                                        chooseChart={chooseChart}
                                    />
                                    :
                                    null
                            }
                        </Grid.Row>
                    </Grid.Column>
                </Grid>
            </div>
        </>
    )
}

function ChartPlaceholder({
    specification,
    data,
    chooseChart
}) {

    const spec = {
        title: "This is a bar chart of a and b",
        width: 400,
        height: 300,
        mark: 'bar',
        encoding: {
            x: { field: 'a', type: 'ordinal' },
            y: { field: 'b', type: 'quantitative' },
        },
        data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array
    }

    const barData = [
        { a: 'A', b: 28 },
        { a: 'B', b: 55 },
        { a: 'C', b: 43 },
        { a: 'D', b: 91 },
        { a: 'E', b: 81 },
        { a: 'F', b: 53 },
        { a: 'G', b: 19 },
        { a: 'H', b: 87 },
        { a: 'I', b: 52 },
    ]

    useEffect(() => {
        specification.width = 400
        specification.width = 300
    }, [])
    return (
        <>
            <div onClick={()=>chooseChart(specification)} className="SelectionPlaceholder">
                <div className="VegaLiteDivSelection">
                    <VegaLite style={{ marginLeft: 10 }} spec={specification} data={{ table: data }} />
                </div>
            </div>
        </>
    )
}

export default ChartSelection