import React from 'react'
import { Grid, Placeholder } from 'semantic-ui-react'
import '../../style.css'

function ChartSelection() {

    return (
        <>
            <div className="ChartSelection">
                <Grid centered={true}>
                    <Grid.Column>
                        <Grid.Row>
                            <ChartPlaceholder
                                chartSelection={true}
                            />
                        </Grid.Row>
                        <Grid.Row>
                            <ChartPlaceholder
                                chartSelection={true}
                            />
                        </Grid.Row>
                        <Grid.Row>
                            <ChartPlaceholder
                                chartSelection={true}
                            />
                        </Grid.Row>
                    </Grid.Column>
                </Grid>
            </div>
        </>
    )
}

function ChartPlaceholder() {
    return (
        <>
            <div className="SelectionPlaceholder">
                
            </div>
        </>
    )
}

export default ChartSelection