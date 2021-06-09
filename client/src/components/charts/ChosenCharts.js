import React, { useEffect } from 'react'
import { Grid } from 'semantic-ui-react'
import '../../style.css'
import { VegaLite } from 'react-vega'

function ChosenCharts({
    charts,
    chartMsg
}) {
    console.log(charts)
    return (
        <>
            <div className="ChosenCharts">
                <Grid centered={true}>
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            {
                                charts[0] ?
                                    <ChartPlaceholder
                                        chartSelection={false}
                                        specification={charts[0]}
                                        data={chartMsg.data}
                                    />
                                    :
                                    null
                            }

                        </Grid.Column>
                        <Grid.Column>
                            {
                                charts[1] ?
                                    <ChartPlaceholder
                                        chartSelection={false}
                                        specification={charts[1]}
                                        data={chartMsg.data}
                                    />
                                    :
                                    null
                            }
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            {
                                charts[2] ?
                                    <ChartPlaceholder
                                        chartSelection={false}
                                        specification={charts[2]}
                                        data={chartMsg.data}
                                    />
                                    :
                                    null
                            }
                        </Grid.Column>
                        <Grid.Column>
                            {
                                charts[3] ?
                                    <ChartPlaceholder
                                        chartSelection={false}
                                        specification={charts[3]}
                                        data={chartMsg.data}
                                    />
                                    :
                                    null
                            }
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </div>
        </>
    )
}

function ChartPlaceholder({
    specification,
    data
}) {
    console.log(specification)
    const spec = {
        title: "This is a bar chart of a and b",
        width: 660,
        height: 520,
        mark: 'bar',
        encoding: {
            x: { field: 'a', type: 'ordinal' },
            y: { field: 'b', type: 'quantitative' },
        },
        data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array
    }

    const barData = {
        table: [
            { a: 'A', b: 28 },
            { a: 'B', b: 55 },
            { a: 'C', b: 43 },
            { a: 'D', b: 91 },
            { a: 'E', b: 81 },
            { a: 'F', b: 53 },
            { a: 'G', b: 19 },
            { a: 'H', b: 87 },
            { a: 'I', b: 52 },
        ],
    }
    specification.width = 660
    specification.height = 520

    return (
        <>
            <div className="ChosenPlaceholder">
                <div className="VegaLiteDivChosen">
                    <VegaLite spec={specification} data={{ table: data }} />
                </div>
            </div>
        </>
    )
}

export default ChosenCharts