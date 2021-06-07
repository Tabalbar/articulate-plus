import React from 'react'
import { Grid } from 'semantic-ui-react'
import '../../style.css'

function ChosenCharts() {
    return (
        <>
            <div className="ChosenCharts">
                <Grid centered={true}>
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            <ChartPlaceholder 
                                chartSelection={false}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <ChartPlaceholder 
                                chartSelection={false}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            <ChartPlaceholder 
                                chartSelection={false}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <ChartPlaceholder 
                                chartSelection={false}
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </div>
        </>
    )
}

function ChartPlaceholder() {
    return (
        <>
            <div className="ChosenPlaceholder"></div>
        </>
    )
}

export default ChosenCharts