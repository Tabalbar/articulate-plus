import React from "react";
import "../../style.css";
import XLSX from "xlsx";
import { Input } from "@chakra-ui/react";

function FileInput({ setChartMsg }) {
  const processData = async (data) => {
    const dataStringLines = data.split(/\r\n|\n/);
    const headers = dataStringLines[0].split(
      /,(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)/
    );

    const list = [];
    for (let i = 1; i < dataStringLines.length; i++) {
      const row = dataStringLines[i].split(
        /,(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)/
      );
      if (headers && row.length == headers.length) {
        const obj = {};
        for (let j = 0; j < headers.length; j++) {
          let d = row[j];
          if (d.length > 0) {
            if (d[0] == '"') d = d.substring(1, d.length - 1);
            if (d[d.length - 1] == '"') d = d.substring(d.length - 2, 1);
          }
          if (headers[j]) {
            obj[headers[j]] = d;
          }
        }

        if (Object.values(obj).filter((x) => x).length > 0) {
          list.push(obj);
        }
      }
    }

    let tmpDataHead = [];
    for (let i = 0; i < 100; i++) {
      tmpDataHead.push(list[i]);
    }
    const response = await fetch("/initialize", {
      method: "POST",
      body: JSON.stringify({ attributes: headers, data: list }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });
    const body = await response.text();
    const { synonymMatrix, featureMatrix } = JSON.parse(body);
    setChartMsg((prev) => {
      return {
        ...prev,
        synonymMatrix: synonymMatrix,
        featureMatrix: featureMatrix,
        attributes: headers,
        data: list,
      };
    });
  };
  const loadData = (e) => {
    e.preventDefault();
    const file = e.target.files[0];
    if (file) {
      var reader = new FileReader();
      reader.onload = function (e) {
        // Use reader.result
        const bstr = e.target.result;
        const wb = XLSX.read(bstr, { type: "binary" });
        /* Get first worksheet */
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        /* Convert array of arrays */
        const data = XLSX.utils.sheet_to_csv(ws, { header: 1 });
        processData(data);
      };
      reader.readAsBinaryString(file);
    }
  };

  return (
    <>
      <Input bg="white" color="black" p={1} type="file" onChange={loadData} />
    </>
  );
}

export default FileInput;
