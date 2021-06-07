import React from 'react'
import "../../style.css"

function ChartPlaceholder ({
    chartSelection
}) {

    return( 
        <>
            <div className={chartSelection ? "SelectionPlaceholder" : "ChosenPlaceholder"}>
            </div>
        </>
    )
}

export default ChartPlaceholder