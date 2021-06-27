import React, { useState } from 'react'
import '../../style.css'
import Window from './Window'
import createDate from '../../helpers/createDate'

function ChosenCharts({
    charts,
    chartMsg,
    setCharts
}) {
    const [, setForceUpdate] = useState(true)
    const handleDelete = (index) => {
        setForceUpdate(prev=>!prev)
        // charts.splice(index, 1)
        // delete charts[index]
        charts[index].visible = false
        charts[index].timeClosed = createDate()
    }   

    return (
            <>

                {charts.map((chart, i) => { 
                    if(chart.visible){ return (
                        <Window 
                        specification={chart} 
                        data={chartMsg.data}
                        handleDelete={handleDelete}
                        index={i}
                        setCharts={setCharts}
                        charts={charts}
                        />
                     
                )} else {return null}})}
        </>
    )
}

// function ChartPlaceholder({
//     specification,
//     data
// }) {
//     const spec = {
//         title: "This is a bar chart of a and b",
//         width: 660,
//         height: 520,
//         mark: 'bar',
//         encoding: {
//             x: { field: 'a', type: 'ordinal' },
//             y: { field: 'b', type: 'quantitative' },
//         },
//         data: { name: 'table' }, // note: vega-lite data attribute is a plain object instead of an array
//     }

//     const barData = {
//         table: [
//             { a: 'A', b: 28 },
//             { a: 'B', b: 55 },
//             { a: 'C', b: 43 },
//             { a: 'D', b: 91 },
//             { a: 'E', b: 81 },
//             { a: 'F', b: 53 },
//             { a: 'G', b: 19 },
//             { a: 'H', b: 87 },
//             { a: 'I', b: 52 },
//         ],
//     }
//     specification.width = 400
//     specification.height = 300

//     return (
//         <>
//             <div className="ChosenPlaceholder">
//                     <Window
//                         specification={specification}
//                         data={data}
//                     />
//                     {/* <VegaLite spec={specification} data={{ table: data }} /> */}
//             </div>
//         </>
//     )
// }

export default ChosenCharts