import React from 'react';
import Draggable from 'react-draggable';
import { VegaLite } from 'react-vega'
import '../../style.css'
import { Box, IconButton, Spacer } from '@chakra-ui/react'
import { CloseIcon } from '@chakra-ui/icons'


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

    }
    eventLogger = (e, data) => {
        let tmpCharts = this.props.charts
        tmpCharts[this.props.index].x = data.x
        tmpCharts[this.props.index].y = data.y
        this.props.setCharts(tmpCharts)
        console.log('Event: ', e);
        console.log('Data: ', data.x);

    };


    onStart(e) {
        let elems = document.getElementsByClassName('react-draggable');
        for(let i = 0; i < elems.length; i++) {
          elems[i].style.zIndex = 10;
          e.currentTarget.style.zIndex = 12;
        }
    }
    


    render() {

        return (
            <>
                <Draggable
                    handle=".handle"
                    grid={[1, 1]}
                    scale={1}
                    bounds={{ bottom: 510, left: 0 }}
                    defaultPosition={{ x: this.props.charts[this.props.index].x, y: this.props.charts[this.props.index].y }}
                    
                    onStart={this.onStart.bind(this)}
                    onDrag={this.handleDrag}
                    onStop={this.eventLogger}>
                    <Box
                        position="absolute"
                        bg="white"
                        overflow="auto"
                        border="1px"
                        boxShadow="2xl"
                        borderColor="black"
                        borderRadius="sm"
                        resize="both"
                        
                        onClick={this.handleClick}
                        style={{ zIndex: this.state.z_index, width: 570, height: 500 }}
                    >
                        <div className="handle" style={{ cursor: "move", width: "auto" }}>
                            <Box borderTopRadius="sm" bg="teal.800"  >
                                <IconButton
                                    colorScheme="red"
                                    borderRadius="sm"
                                    // ml={"38rem"}
                                    aria-label="Search database"
                                    icon={<CloseIcon />}
                                    onClick={() => this.props.handleDelete(this.props.index)}
                                />
                                {/* <Menu.Item
                                icon="x"
                                style={{ background: "red" }}
                                position="right"
                            /> */}
                            </Box>
                        <VegaLite width={420} height={350} spec={this.props.specification} data={{ table: this.props.data }} />
                        </div>

                    </Box>
                </Draggable>

            </>
        );
    }
}


export default React.memo(Window)