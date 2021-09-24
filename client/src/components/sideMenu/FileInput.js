import React, { useState } from "react";
import "../../style.css";
import XLSX from "xlsx";
import { Input } from "@chakra-ui/react";
import { chartObjState } from "../../shared/chartObjState";
import { useRecoilState } from "recoil";
import ChartObj from "../../shared/ChartObj";

function FileInput({ setChartMsg }) {
  const loadData = async (e) => {
    ChartObj.initialize();

    const something = await ChartObj.loadData(e);
    something.featurematrix;
  };

  return (
    <>
      <Input bg="white" color="black" p={1} type="file" onChange={loadData} />
    </>
  );
}

export default FileInput;
