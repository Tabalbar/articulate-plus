import React from 'react';
import Draggable from 'react-draggable';
import { VegaLite } from 'react-vega'
import '../../style.css'
import { Menu } from 'semantic-ui-react'


// function Window({
//     specification,
//     data,
//     handleDelete,
//     index
// }) {
//     const [position, setPosition] = useState({ x: 0, y: 0 })

//     console.log(position)
//     return (
//         <Window2
//             specification={specification}
//             data={data}
//             handleDelete={handleDelete}
//             index={index}
//             setPosition={setPosition}
//             position={position}
//         />
//     )
// }

class Window extends React.PureComponent {
    constructor(props) {
        super(props);
        // Don't call this.setState() here!
        this.state = { z_index: 0 };
        this.handleClick = this.handleClick.bind(this);
    }
    eventLogger = (e, data) => {
        let tmpCharts = this.props.charts
        tmpCharts[this.props.index].x = data.x
        tmpCharts[this.props.index].y = data.y
        this.props.setCharts(tmpCharts)
        console.log('Event: ', e);
        console.log('Data: ', data);
    };
    handleClick = () => {
        this.setState({ z_index: 0 })
        this.setState({ z_index: 1 })
    }

    render() {
        console.log(this.props.charts)

        return (
            <>
                <Draggable
                    handle=".handle"
                    grid={[1, 1]}
                    scale={1}
                    bounds={{ bottom: 385, left: 0 }}
                    defaultPosition={{ x: this.props.charts[this.props.index].x, y: this.props.charts[this.props.index].y }}
                    // position={null}
                    onStart={this.handleStart}
                    onDrag={this.handleDrag}
                    onStop={this.eventLogger}>
                    <div className="Charts" onClick={this.handleClick} style={{ zIndex: this.state.z_index, width: 570, height: 500 }}>
                        <div className="handle" style={{cursor: "move"}}>
                            <Menu size="small" inverted >
                                <Menu.Item
                                    icon="x"
                                    style={{background: "red"}}
                                    onClick={() => this.props.handleDelete(this.props.index)}
                                    position="right"
                                />
                            </Menu>
                        </div>
                        <VegaLite spec={this.props.specification} data={{ table: this.props.data }} />

                    </div>
                </Draggable>

            </>
        );
    }
}

export default React.memo(Window)