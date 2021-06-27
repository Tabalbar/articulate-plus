import React, { useEffect } from 'react'
import { Grid } from 'semantic-ui-react'
import StreamGraph from '../components/diagnostics/StreamGraph'

function Diagnostics({
    overHearingData,
    chartMsg
}) {



    // useEffect(() => {

    // }, [overHearingData])

    return (
        <>
            {
                chartMsg.attributes.length ?
                    <StreamGraph
                        overHearingData={overHearingData}
                        attributes={chartMsg.attributes}
                        synonymAttributes={chartMsg.synonymMatrix}
                        featureAttributes={chartMsg.featureMatrix}
                    />
                    :
                    null
            }

        </>
    )
}

export default Diagnostics