/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
let devPivotData = true;

const fs = require("fs");
const path = require("path");
const csv = require("fast-csv");
let data = [];

function readCSV() {
  let isCommandData = [];
  let promise = new Promise((resolve, reject) => {
    fs.createReadStream(path.resolve(__dirname, "../server/assets/val.csv"))
      .pipe(csv.parse({ headers: true }))
      .on("data", (row) => {
        isCommandData.push(row);
      })
      .on("end", () => {
        resolve(isCommandData);
      });
  });
  return promise;
}
// (async () => {
//   await neuralNetworkData().then((data) => {
//     console.log(data);
//   });
// })();
module.exports = () => {
  let isCommandData = [];
  let promise = new Promise((resolve, reject) => {
    fs.createReadStream(
      path.resolve(__dirname, "../server/assets/isCommandData5.csv")
    )
      .pipe(csv.parse({ headers: true }))
      .on("data", (row) => {
        isCommandData.push(row);
      })
      .on("end", () => {
        resolve(isCommandData);
      });
  });
  return promise;
  // if (devPivotData) {
  // await readCSV().then((data) => {
  //   console.log(data);
  //   // return data;
  // });
  // console.log(data);
  // return data;
  // } else {
  //   return new Promise((resolve, reject) => {
  //     fs.readFile(
  //       path.resolve(__dirname, "../server/assets/isCommandData5.csv"),
  //       "utf8",
  //       (err, data) => {
  //         if (err) {
  //           reject(err);
  //         }
  //         resolve(data);
  //       }
  //     );
  //   });
  // }
};

// if (devPivotData) {
//   module.exports = {
//     queries: [],
//     answers: ["bar", "line", "map", "pivot", "heatmap", "none"],
//   };

// } else {
//   module.exports = {
//     queries: [
//       { query: "show me the distribution of nominal", chartType: "bar" },
//       { query: "show me a graph with nominal and nominal", chartType: "bar" },
//       { query: "show me a chart of nominal and nominal", chartType: "bar" },

//       {
//         query: "I want to see the comparison of nominal over time",
//         chartType: "line",
//       },
//       { query: "show me nominal by date", chartType: "line" },
//       {
//         query: "show me the comparison of nominal over temporal",
//         chartType: "line",
//       },
//       {
//         query: "Show me the temporal over the year of nominal and quantitative",
//         chartType: "line",
//       },
//       {
//         query: "Show me where is nominal",
//         chartType: "map",
//       },
//       {
//         query: "Where is nominal",
//         chartType: "map",
//       },
//       { query: "I want to see nominal on the map", chartType: "map" },
//     ],
//     answers: ["bar", "line", "map"],
//     pivotChartQueries: [
//       { query: "show me this but for nominal", chartType: "pivot" },
//       { query: "I want to see this but for nominal", chartType: "pivot" },
//       { query: "can i see this but filtered by nominal", chartType: "pivot" },
//     ],
//   };
// }

//   {
//     query: "I want to see quantitative by quantitative",
//     chartType: "scatter",
//   },
//   {
//     query: "show me the relationship of quantitative and quantitative",
//     chartType: "scatter",
//   },
//   { query: "what is the quantitative of quantitative", chartType: "scatter" },
// {
//   query: "show me the correlation of quantiative and quantitative",
//   chartType: "heatmap",
// },
// { query: "show me quantitative by quantitative", chartType: "heatmap" },
// manager.addDocument(
//   "en",
//   "I want to see quantitative by quantitative",
//   "scatter"
// );
// manager.addDocument(
//   "en",
//   "show me the relationship of quantitative and quantitative",
//   "scatter"
// );
// manager.addDocument(
//   "en",
//   "what is the quantitative of quantitative",
//   "scatter"
// );
// manager.addAnswer("en", "scatter", "scatter");

// manager.addDocument(
//   "en",
//   "show me the correlation of quantiative and quantitative",
//   "heatmap"
// );
// manager.addDocument("en", "show me quantitative by quantitative", "heatmap");
// manager.addAnswer("en", "heatmap", "heatmap");

// module.exports = {
//   queries: [
//     { query: "show me the distribution of nominal", chartType: "bar" },
//     { query: "show me a chart of nominal", chartType: "bar" },
//     { query: "show me a graph with nominal and nominal", chartType: "bar" },
//     { query: "show me a chart of nominal and nominal", chartType: "heatmap" },
//     {
//       query: "what is the correlation between nominal and nominal",
//       chartType: "heatmap",
//     },
//     {
//       query: "I want to see the comparison of nominal over time",
//       chartType: "line",
//     },
//     { query: "show me quantitative by temporal", chartType: "line" },
//     {
//       query: "show me the quantitative for nominal",
//       chartType: "line",
//     },
//     {
//       query: "where are the quantitative",
//       chartType: "line",
//     },
//     {
//       query: "show me the quantitative",
//       chartType: "line",
//     },
//     {
//       query: "Show me the temporal over the year of nominal and quantitative",
//       chartType: "line",
//     },
//     {
//       query: "Show me where is nominal",
//       chartType: "map",
//     },
//     {
//       query: "Where is nominal",
//       chartType: "map",
//     },
//     { query: "I want to see nominal on the map", chartType: "map" },
//     // { query: "show me this but for nominal", chartType: "pivot" },
//     // { query: "I want to see this but for nominal", chartType: "pivot" },
//     // { query: "can i see this but filtered by nominal", chartType: "pivot" },
//   ],
// answers: ["bar", "line", "map", "pivot", "heatmap"],
//   // pivotChartQueries: [
//   //   { query: "show me this but for nominal", chartType: "pivot" },
//   //   { query: "I want to see this but for nominal", chartType: "pivot" },
//   //   { query: "can i see this but filtered by nominal", chartType: "pivot" },
//   // ],
// };
