// import React, { useEffect, useRef, useState } from "react";
// import "../../style.css";
// import { VegaLite } from "react-vega";
// import { Box, HStack, VStack } from "@chakra-ui/react";
// import processData from "../../helpers/processData";

// function ChartSelection({ chartMsg, chooseChart, modifiedChartOptions }) {
//   const slideTimer = useRef(null);
//   useEffect(() => {
//     if (slideTimer) {
//       clearInterval(slideTimer.current);
//     }
//     let scrollableElement = document.getElementById("scrollable");
//     scrollableElement.scrollLeft =
//       scrollableElement.scrollWidth - scrollableElement.clientWidth;
//     slideTimer.current = setInterval(() => {
//       scrollableElement.scrollLeft += 5;
//       if (
//         scrollableElement.scrollLeft + scrollableElement.clientWidth >=
//         scrollableElement.scrollWidth - 10
//       ) {
//         clearInterval(slideTimer.current);
//       }
//     }, 35);
//   }, [chartMsg.charts]);

//   return (
//     <>
//       <Box
//         // position="absolute"
//         // bottom="0"
//         // bg="gray.700"
//         // width="100vw"
//         // height="50rem"
//         // zIndex="1"
//         // right="0"
//         // borderLeft="5px"
//         // borderColor="black"
//         position="absolute"
//         // bottom="0"
//         bg="gray.700"
//         height="100vh"
//         width="75rem"
//         // zIndex="1"
//         right="0"
//         borderLeft="5px"
//         borderColor="black"
//       >
//         <Box
//           // zIndex={3}
//           // className="scrollBarX"
//           // bottom="0"
//           // width="100vw"
//           // height="50rem"
//           // display="flex"
//           // id="scrollable"
//           zIndex={3}
//           className="scrollBarY"
//           right="0"
//           height="100vh"
//           width="75rem"
//           display="flex"
//           id="scrollable"
//           borderLeft={2}
//           borderColor="black"
//         >
//           <VStack>
//             {chartMsg.charts.map((chart, index) => {
//               return (
//                 <>
//                   {chart ? (
//                     <Box
//                       onMouseEnter={() => {
//                         clearInterval(slideTimer.current);
//                         let scrollableElement =
//                           document.getElementById("scrollable");
//                       }}
//                       zIndex={0}
//                       p={2}
//                       key={index}
//                     >
//                       <ChartPlaceholder
//                         key={index}
//                         specification={chart}
//                         data={chartMsg.data}
//                         chooseChart={chooseChart}
//                         modifiedChartOptions={modifiedChartOptions}
//                       />
//                     </Box>
//                   ) : null}
//                 </>
//               );
//             })}
//           </VStack>
//         </Box>
//       </Box>
//     </>
//   );
// }

// function ChartPlaceholder({
//   specification,
//   data,
//   chooseChart,
//   modifiedChartOptions,
// }) {
//   const [startTime, setStartTime] = useState("");
//   const [spec, setSpec] = useState(specification);
//   const [hovered, setHovered] = useState(false);
//   const [clicked, setClicked] = useState(false);
//   const [chartData, setChartData] = useState(data);
//   useEffect(() => {
//     if (modifiedChartOptions.useCovidDataset == true) {
//       console.log("true");

//       if (
//         specification.hasOwnProperty("layer") ||
//         specification.mark == "bar"
//       ) {
//         // specification.transform.push({
//         //   type: "aggregate",
//         //   fields: ["access to doctors"],
//         //   ops: ["distinct"],
//         // });
//         specification.transform = [];
//         console.log(specification.transform);

//         // console.log("fetching");
//         // specification.fetchedURL = true;
//         // fetch(
//         //   "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
//         // )
//         //   .then((response) => response.text())
//         //   .then(async (csvData) => setChartData(await processData(csvData)));
//       }
//     }
//   }, []);
//   const startTimer = () => {
//     setStartTime(performance.now());
//     setHovered(true);
//   };
//   const endTimer = () => {
//     var timeDiff = performance.now() - startTime;
//     timeDiff /= 1000;
//     specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2));
//     setHovered(false);
//   };
//   const testClick = (e) => {
//     specification.x = e.clientX - 250;
//     specification.y = e.clientY - 800;
//     console.log(specification);
//   };

//   return (
//     <>
//       <Box
//         bg="transparent"
//         zIndex={hovered ? 10 : 3}
//         onClick={
//           specification.visible
//             ? null
//             : (e) => {
//                 testClick(e);
//                 endTimer();
//                 chooseChart(specification);
//                 setClicked(true);
//               }
//         }
//         onMouseOver={startTimer}
//         onMouseLeave={endTimer}
//         opacity={specification.visible ? 0.5 : null}
//       >
//         <Box bg="white" borderColor="black" borderWidth="3px" rounded="lg">
//           <VegaLite spec={spec} data={{ table: chartData }} />
//         </Box>
//       </Box>
//     </>
//   );
// }

// export default ChartSelection;

import React, { useEffect, useRef, useState } from "react";
import "../../style.css";
import { VegaLite } from "react-vega";
import { Box, HStack } from "@chakra-ui/react";
import processData from "../../helpers/processData";

function ChartSelection({ chartMsg, chooseChart, modifiedChartOptions }) {
  const slideTimer = useRef(null);
  useEffect(() => {
    if (slideTimer) {
      clearInterval(slideTimer.current);
    }
    let scrollableElement = document.getElementById("scrollable");
    scrollableElement.scrollLeft =
      scrollableElement.scrollWidth - scrollableElement.clientWidth;
    slideTimer.current = setInterval(() => {
      scrollableElement.scrollLeft += 5;
      if (
        scrollableElement.scrollLeft + scrollableElement.clientWidth >=
        scrollableElement.scrollWidth - 10
      ) {
        clearInterval(slideTimer.current);
      }
    }, 35);
  }, [chartMsg.charts]);

  return (
    <>
      <Box
        position="absolute"
        bottom="0"
        bg="gray.700"
        width="100vw"
        height="50rem"
        zIndex="1"
        right="0"
        borderTop="2px"
        borderColor="black"
      >
        <Box
          zIndex={3}
          className="scrollBarX"
          bottom="0"
          width="100vw"
          height="50rem"
          display="flex"
          id="scrollable"
        >
          <HStack spacing={100}>
            {chartMsg.charts.map((chart, index) => {
              return (
                <>
                  {chart ? (
                    <Box
                      onMouseEnter={() => {
                        clearInterval(slideTimer.current);
                        let scrollableElement =
                          document.getElementById("scrollable");
                      }}
                      zIndex={20}
                      p={2}
                      key={index}
                    >
                      <ChartPlaceholder
                        key={index}
                        specification={chart}
                        data={chartMsg.data}
                        chooseChart={chooseChart}
                        modifiedChartOptions={modifiedChartOptions}
                      />
                    </Box>
                  ) : null}
                </>
              );
            })}
          </HStack>
        </Box>
      </Box>
    </>
  );
}

function ChartPlaceholder({
  specification,
  data,
  chooseChart,
  modifiedChartOptions,
}) {
  const [startTime, setStartTime] = useState("");
  const [spec, setSpec] = useState(specification);
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);
  const [chartData, setChartData] = useState(data);
  useEffect(() => {
    if (modifiedChartOptions.useCovidDataset == true) {
      if (specification.hasOwnProperty("layer")) {
        // specification.transform.push({
        //   type: "aggregate",
        //   fields: ["access to doctors"],
        //   ops: ["distinct"],
        // });
        specification.transform = [];

        // console.log("fetching");
        specification.fetchedURL = true;
        fetch(
          "https://raw.githubusercontent.com/Tabalbar/Articulate/main/NEW_Covid_Data.csv"
        )
          .then((response) => response.text())
          .then(async (csvData) => setChartData(await processData(csvData)));
      }
    }
  }, []);
  const startTimer = () => {
    setStartTime(performance.now());
    setHovered(true);
  };
  const endTimer = () => {
    var timeDiff = performance.now() - startTime;
    timeDiff /= 1000;
    specification.timeSpentHovered += parseFloat(Number(timeDiff).toFixed(2));
    setHovered(false);
  };
  const testClick = (e) => {
    specification.x = e.clientX - 250;
    specification.y = e.clientY - 800;
  };

  return (
    <>
      <Box
        bg="transparent"
        zIndex={hovered ? 10 : 3}
        onClick={
          specification.visible
            ? null
            : (e) => {
                testClick(e);
                endTimer();
                chooseChart(specification);
                setClicked(true);
              }
        }
        onMouseOver={startTimer}
        onMouseLeave={endTimer}
        opacity={specification.visible ? 0.5 : null}
      >
        <Box bg="white" borderColor="black" borderWidth="3px" rounded="lg">
          <VegaLite spec={spec} data={{ table: chartData }} />
        </Box>
      </Box>
    </>
  );
}

export default ChartSelection;
