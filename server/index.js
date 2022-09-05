/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const express = require("express");
const PORT = process.env.PORT || 6000;
const app = express();
const path = require("path");
const ExtendNLP = require("./Pre-processing/ExtendNLP");
var request = require("request-promise");

app.use(express.json({ limit: "500mb" }));
app.use(express.urlencoded({ extended: true, limit: "500mb" }));

app.use(express.static(path.resolve(__dirname, "../client/build")));
const { NlpManager } = require("node-nlp");

const manager = new NlpManager({
  languages: ["en"],
  forceNER: true,
  nlu: { log: false },
});

const neuralNetworkData = require("./neuralNetworkData");
neuralNetworkData().then(async (data) => {
  let answers = ["bar", "line", "map", "pivot", "heatmap"];
  for (let i = 0; i < data.length; i++) {
    manager.addDocument("en", data[i].queries, data[i].chartType);
  }
  for (let i = 0; i < answers.length; i++) {
    manager.addAnswer("en", answers[i], answers[i]);
  }
  await manager.train();
  manager.save();
});
// for (let i = 0; i < neuralNetworkData.queries.length; i++) {
//   console.log(neuralNetworkData.queries[i].query);
//   manager.addDocument(
//     "en",
//     neuralNetworkData.queries[i].query,
//     neuralNetworkData.queries[i].chartType
//   );
// }

// for (let i = 0; i < neuralNetworkData.answers.length; i++) {
//   manager.addAnswer(
//     "en",
//     neuralNetworkData.answers[i],
//     neuralNetworkData.answers[i]
//   );
// }

// Train and save the model.
// (async () => {
//   await manager.train();
//   manager.save();
// })();
//***************** */

/**
 * Initialize
 */
app.post("/initialize", (req, res) => {
  // console.log(req.body)
  const modifiedChartOptions = req.body.modifiedChartOptions;
  console.log("Initialized Attributes");
  const { featureMatrix, synonymMatrix } = ExtendNLP(
    req.body.attributes,
    req.body.data
  );
  if (featureMatrix === null || synonymMatrix === null) {
    console.log("Error in pre-processing");
    res.status(405).send("Error in pre-processing");
  }
  res.json({ featureMatrix: featureMatrix, synonymMatrix: synonymMatrix });
});

/**
 * Generalize the command and send through chartMaker pipeline
 */
const generalizeCommand = require("./generalizeCommand");
const getExplicitChartType = require("./createChartsV3/charts/helpers/getExplicitChartType");
const CompareCharts = require("./CompareCharts");
const countHeaderFrequency = require("./createChartsV3/overhearing/countHeaderFrequency");
const constructPythonCommand = require("./python/constructPythonCommand");

const pivotChartsV2 = require("./createChartsV3/pivotCharts/pivotChartsV2");

const createCharts = require("./createChartsV3/createCharts");
const chartOptions = require("./createChartsV3/charts/helpers/chartOptions");

let replaceWords = [{ wordFound: "hi", replaceWith: "high" }];

function difficultPhrasedWords(command) {
  let words = command.split(" ");
  words = words.map((word) =>
    replaceWords.map((replaceWord) =>
      replaceWord.wordFound == word ? replaceWord.replaceWith : word
    )
  );

  if (words.length === 0) {
    return "";
  } else if (words.length === 1) {
    return words[0][0];
  } else {
    return words.reduce(
      (previousWord, nextWord) => previousWord + " " + nextWord
    );
  }
}

app.post("/createCharts", async (req, res) => {
  let chartMsg = req.body.chartMsg;
  let options = req.body.modifiedChartOptions;
  let chosenCharts = req.body.selectedCharts;
  let pivotTheseCharts = req.body.pivotTheseCharts;
  //Remove stop words and change known synonyms
  chartMsg.command = difficultPhrasedWords(chartMsg.command);
  let availableCharts = chartOptions(chartMsg.data);

  //Explicit chart commands
  let { generalizedCommand } = generalizeCommand(
    chartMsg.command,
    chartMsg.attributes,
    chartMsg.data,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix
  );
  chartMsg.generalizedCommand = generalizedCommand;

  let response = await manager.process("en", chartMsg.generalizedCommand);
  let isCommand = "None";
  classifications = response.classifications;

  for (let i = 0; i < classifications.length; i++) {
    if (
      classifications[i].score > 0.8 &&
      classifications[i].intent !== "none"
    ) {
      for (let j = 0; j < availableCharts.length; j++) {
        if (availableCharts[j].mark === classifications[i].intent) {
          isCommand = classifications[i].intent;
          break;
        }
      }
    }
  }

  let intent = getExplicitChartType(chartMsg.command, availableCharts);
  if (intent !== false) {
    isCommand = intent;
  }

  if (chartMsg.command === "random") {
    isCommand = "random";
  }

  if (isCommand === "None" || isCommand === "none") {
    chartMsg.errMsg = "none";
    res.send({ chartMsg: chartMsg });
  } else {
    if (isCommand === "random") {
      let randomizedAvailableChartTypes = availableCharts.filter(
        (chart) => chart.available === true
      );
      isCommand =
        randomizedAvailableChartTypes[
          Math.floor(Math.random() * randomizedAvailableChartTypes.length)
        ].mark;
    } else {
      chartMsg.explicitChart = createCharts(isCommand, chartMsg, {
        useCovidDataset: options.useCovidDataset,
        sentimentAnalysis: false,
        window: {
          toggle: false,
          pastSentences: 0,
        },
        neuralNetwork: false,
        useSynonyms: false,
        randomCharts: {
          toggle: false,
          minutes: 10,
        },
        threshold: 3,
        filter: {
          toggle: false,
          pastSentences: 0,
          threshold: 5,
        },
        pivotCharts: false,
      });
    }

    chartMsg.mainAIOverhearing = createCharts(isCommand, chartMsg, options);
    CompareCharts(chartMsg, options, chosenCharts);

    chartMsg.mainAIOverhearingCount = countHeaderFrequency(chartMsg, options);
    chartMsg.total = countHeaderFrequency(chartMsg, {
      sentimentAnalysis: false,
      window: {
        toggle: true,
        pastSentences: 99999,
      },
      neuralNetwork: true,
      filter: {
        toggle: false,
        pastSentences: options.filter.pastSentences,
        threshold: options.filter.threshold,
      },
    });
    // chartMsg.errMsg = "";
    res.send({ chartMsg });
  }
});

// /**
//  * Getting expicit mark type
//  */
// //Check if pivot
// if (chartMsg.command == "random") {
//   let intent = chartOptions[Math.floor(Math.random() * 5)];
//   chartMsg.randomCharts = createCharts(intent.mark, chartMsg, options);
// } else if (pivotTheseCharts.length > 0) {
//   chartMsg.pivotChart = pivotChartsV2(pivotTheseCharts, chartMsg, options);
// } else if (intent) {
// } else {
//   if (intent !== "None") {
//     chartMsg.mainAI = createCharts(intent, chartMsg, {
//       useCovidDataset: options.useCovidDataset,
//       sentimentAnalysis: false,
//       window: {
//         toggle: false,
//         pastSentences: 0,
//       },
//       neuralNetwork: true,
//       useSynonyms: true,
//       randomCharts: {
//         toggle: false,
//         minutes: 10,
//       },
//       threshold: 3,
//       filter: {
//         toggle: false,
//         pastSentences: 0,
//         threshold: 5,
//       },
//       pivotCharts: false,
//     });
//     chartMsg.mainAIOverhearing = createCharts(intent, chartMsg, options);
//   } else {
//     //If Neural Network has no match for intent, no charts are made
//     chartMsg.explicitChart = "";
//     chartMsg.inferredChart = "";
//     chartMsg.modifiedChart = "";
//   }
// }

const fs = require("fs");

const content = "Some content!";

app.post("/log", function (req, res) {
  // console.log(JSON.stringify(req.body.content));
  fs.writeFile(req.body.fileName, JSON.stringify(req.body.content), (err) => {
    if (err) {
      console.error(err);
      return;
    }
    //file written successfully
  });
  res.send("Success");
});

app.post("/flask", async function (req, res) {
  let chartMsg = req.body.chartMsg;
  let command = chartMsg.command;
  if (command == "random") {
    chartMsg.pythonCharts = [];
    res.send(chartMsg);
  } else {
    let options = {
      method: "POST",
      uri: "http://localhost:5000/",
      body: command,
      json: true, // Automatically stringifies the body to JSON
    };

    let returndata = null;
    let constructedPythonCommand;
    let sendrequest = await request(options)
      .then(function (parsedBody) {
        // console.log(parsedBody); // parsedBody contains the data sent back from the Flask server
        returndata = parsedBody; // do something with this data, here I'm assigning it to a variable.
        let constructedCommand = constructPythonCommand(parsedBody, chartMsg);
        chartMsg.command = constructedCommand.command;
        chartMsg.pythonCharts = createCharts(
          constructedCommand.plotType,
          chartMsg,
          {
            useCovidDataset: options.useCovidDataset,
            sentimentAnalysis: false,
            window: {
              toggle: false,
              pastSentences: 0,
            },
            neuralNetwork: false,
            useSynonyms: false,
            randomCharts: {
              toggle: false,
              minutes: 10,
            },
            threshold: 3,
            filter: {
              toggle: false,
              pastSentences: 0,
              threshold: 5,
            },
            pivotCharts: false,
          },
          true
        );
        console.log("returned from python");
      })
      .catch(function (err) {
        console.log("error, Python server doesn't understand");
        console.log(err);
        // res.send({ message: "error" });
      });

    res.send(chartMsg);
  }
});

// app.post("/flask", async function (req, res) {
//   let chartMsg = req.body.chartMsg;
//   let command = chartMsg.command;
//   if (command == "random") {
//     res.send({ charts: [] });
//   }
//   console.log(command);

//   let options = {
//     method: "POST",
//     uri: "http://localhost:5000/",
//     body: command,
//     json: true, // Automatically stringifies the body to JSON
//   };

//   let returndata;
//   let constructedPythonCommand;
//   let sendrequest = await request(options)
//     .then(function (parsedBody) {
//       // console.log(parsedBody); // parsedBody contains the data sent back from the Flask server
//       returndata = parsedBody; // do something with this data, here I'm assigning it to a variable.
//       constructedPythonCommand = constructPythonCommand(parsedBody);
//     })
//     .catch(function (err) {
//       console.log(err);
//     });

//     if (returndata == "" || returndata == null) {
//     console.log("fired");
//     res.send({ message: "" });
//   } else {
//     res.send(returndata);
//   }
// });

// All other GET requests not handled before will return our React app
app.get("*", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../client/build", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`);
});
process.on("SIGINT", function () {
  // this is only called on ctrl+c, not restart
  process.kill(process.pid, "SIGINT");
  process.exit();
});
process.once("SIGUSR2", function () {
  process.kill(process.pid, "SIGUSR2");
  process.exit();
});
