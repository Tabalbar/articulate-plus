const express = require("express");
const PORT = process.env.PORT || 6000;
const app = express();
const path = require("path");
const ExtendNLP = require("./Pre-processing/ExtendNLP");
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

for (let i = 0; i < neuralNetworkData.queries.length; i++) {
  manager.addDocument(
    "en",
    neuralNetworkData.queries[i].query,
    neuralNetworkData.queries[i].chartType
  );
}

for (let i = 0; i < neuralNetworkData.answers.length; i++) {
  manager.addAnswer(
    "en",
    neuralNetworkData.answers[i],
    neuralNetworkData.answers[i]
  );
}

// Train and save the model.
(async () => {
  await manager.train();
  manager.save();
})();
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
  // if (modifiedChartOptions.pivotCharts) {
  //   for (let i = 0; i < neuralNetworkData.pivotChartQueries.length; i++) {
  //     manager.addDocument(
  //       "en",
  //       neuralNetworkData.pivotChartQueries[i].query,
  //       neuralNetworkData.pivotChartQueries[i].chartType
  //     );
  //   }
  //   manager.addAnswer("en", "pivot", "pivot");
  //   (async () => {
  //     await manager.train();
  //     manager.save();
  //   })();
  //   console.log("Added Pivot to Neural Network");
  // }
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
const getExplicitChartType = require("./createCharts/explicit/ExplicitChart");
const CompareCharts = require("./CompareCharts");
const countHeaderFrequency = require("./createCharts/countHeaderFrequency");

// const createCharts = require("./createCharts/createCharts");

// const explicitChart = require("./oldChartMaker/explicit/explicitChart");
// const inferredChart = require("./oldChartMaker/inferred/inferredChart");
// const modifiedChart = require("./oldChartMaker/modified/modifiedChart");
const pivotChartsV2 = require("./createCharts/pivotCharts/pivotChartsV2");

const createCharts = require("./createChartsV3/createCharts");
const chartOptions = require("./createCharts/explicit/chartOptions");

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

  //Explicit chart commands
  let { generalizedCommand } = generalizeCommand(
    chartMsg.command,
    chartMsg.attributes,
    chartMsg.data,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix
  );
  chartMsg.generalizedCommand = generalizedCommand;

  /**
   * Getting expicit mark type
   */
  let intent = getExplicitChartType(chartMsg.command);
  //Check if pivot
  if (chartMsg.command == "random") {
    let intent = chartOptions[Math.floor(Math.random() * 5)];
    chartMsg.randomCharts = createCharts(intent.mark, chartMsg, options);
  } else if (pivotTheseCharts.length > 0) {
    chartMsg.pivotChart = pivotChartsV2(pivotTheseCharts, chartMsg, options);
  } else if (intent) {
    chartMsg.explicitChart = createCharts(intent, chartMsg, {
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
    chartMsg.mainAI = createCharts(intent, chartMsg, {
      useCovidDataset: options.useCovidDataset,
      sentimentAnalysis: false,
      window: {
        toggle: false,
        pastSentences: 0,
      },
      neuralNetwork: true,
      useSynonyms: true,
      randomCharts: {
        toggle: true,
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
    chartMsg.mainAIOverhearing = createCharts(intent, chartMsg, options);
  } else {
    intent = (await manager.process("en", chartMsg.generalizedCommand)).intent;
    if (intent !== "None") {
      chartMsg.mainAI = createCharts(intent, chartMsg, {
        useCovidDataset: options.useCovidDataset,
        sentimentAnalysis: false,
        window: {
          toggle: false,
          pastSentences: 0,
        },
        neuralNetwork: true,
        useSynonyms: true,
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
      chartMsg.mainAIOverhearing = createCharts(intent, chartMsg, options);
    } else {
      //If Neural Network has no match for intent, no charts are made
      chartMsg.explicitChart = "";
      chartMsg.inferredChart = "";
      chartMsg.modifiedChart = "";
    }
  }
  CompareCharts(chartMsg, options, chosenCharts);

  chartMsg.mainAIOverhearingCount = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    options
  );
  chartMsg.total = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    {
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
    }
  );
  res.send({ chartMsg });
});

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
