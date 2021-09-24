import React, { useState } from "react";
import "../../style.css";
import XLSX from "xlsx";
import { Input } from "@chakra-ui/react";
import { chartObjState } from "../../shared/chartObjState";
import { useRecoilState } from "recoil";
import ChartObj from "../../shared/ChartObj";

function FileInput({ setChartMsg }) {
  // const [chart, setChart] = useRecoilState(chartObjState);

  // const loadData = async (e) => {
  //   // ChartObj.initialize();

  //   const response = chart.loadData(e);
  //   setChart(prev=> {return({...prev, })}
  //   // if(response)
  // };

  return <></>;
}

export default FileInput;
