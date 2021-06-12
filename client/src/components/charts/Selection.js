import React, { useEffect } from 'react'
import { Grid, Placeholder } from 'semantic-ui-react'
import '../../style.css'
import { VegaLite } from 'react-vega'
import Attributes from '../TreeMenu'


function ChartSelection({
    chartMsg,
    chooseChart
}) {

    return (
        <>
            <div className="ChartSelection">
                <Grid centered={true}>
                    <Grid.Row columns={4}>
                        <Grid.Column>
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

                        </Grid.Column>
                        <Grid.Column>
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
                        </Grid.Column>
                        <Grid.Column>
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
                        </Grid.Column>
                        <Grid.Column>
                            <Attributes/>
                        </Grid.Column>
                    </Grid.Row>
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

    specification.x = 0
    specification.y = 0
    return (
        <>
            <div onClick={() => chooseChart(specification)} className="SelectionPlaceholder">
                <div className="VegaLiteDivSelection">
                    <VegaLite style={{ marginLeft: 10 }} spec={specification} data={{ table: data }} />
                </div>
            </div>
        </>
    )
}

export default ChartSelection

