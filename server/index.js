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

const createCharts = require("./createCharts/createCharts");
const ChartInfo = require("../newCreateCharts/chartObj/ChartInfo");

const explicitChart = require("./oldChartMaker/explicit/explicitChart");
const inferredChart = require("./oldChartMaker/inferred/inferredChart");
const modifiedChart = require("./oldChartMaker/modified/modifiedChart");
const pivotCharts = require("./createCharts/pivotCharts/pivotCharts");

app.post("/createCharts", async (req, res) => {
  let chartMsg = req.body.chartMsg;
  let modifiedChartOptions = req.body.modifiedChartOptions;
  let pivotTheseCharts = req.body.pivotTheseCharts;
  //Remove stop words and change known synonyms

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
   * Getting ExplicitChart
   */
  let intent = getExplicitChartType(chartMsg.command);

  if (!intent) {
    intent = (await manager.process("en", chartMsg.generalizedCommand)).intent;
  }
  if (pivotTheseCharts.length > 0) {
    chartMsg.pivotChart = pivotCharts(pivotTheseCharts, chartMsg);
  } else if (intent !== "None") {
    if (modifiedChartOptions.useCovidDataset == true) {
      /**
       * Explicit Chart
       */
      chartMsg.explicitChart = createCharts(intent, chartMsg, {
        sentimentAnalysis: false,
        window: {
          toggle: false,
          pastSentences: 99999,
        },
        neuralNetwork: false,
        threshold: 0,
        filter: {
          toggle: false,
          pastSentences: 99999,
          threshold: 999,
        },
      });

      /**
       * Window + Sentiment Chart
       */
      chartMsg.inferredChart = createCharts(intent, chartMsg, {
        sentimentAnalysis: true,
        window: {
          toggle: modifiedChartOptions.window.toggle,
          pastSentences: modifiedChartOptions.window.pastSentences,
        },
        neuralNetwork: modifiedChartOptions.neuralNetwork,
        threshold: modifiedChartOptions.threshold,
        filter: {
          toggle: modifiedChartOptions.filter.toggle,
          pastSentences: modifiedChartOptions.filter.pastSentences,
          threshold: modifiedChartOptions.filter.threshold,
        },
      });

      /**
       * Window Chart
       */
      chartMsg.modifiedChart = createCharts(
        intent,
        chartMsg,
        modifiedChartOptions
      );
    } else {
      chartMsg.inferredChart = inferredChart(intent, chartMsg);

      chartMsg.explicitChart = explicitChart(intent, chartMsg);
      chartMsg.modifiedChart = modifiedChart(
        intent,
        chartMsg,
        modifiedChartOptions
      );
    }
    CompareCharts(chartMsg);
  } else {
    //If Neural Network has no match for intent, no charts are made
    chartMsg.explicitChart = "";
    chartMsg.inferredChart = "";
    chartMsg.modifiedChart = "";
  }

  chartMsg.window_sentiment = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    {
      sentimentAnalysis: true,
      window: {
        toggle: true,
        pastSentences: modifiedChartOptions.window.pastSentences,
      },
      neuralNetwork: true,
      filter: {
        toggle: modifiedChartOptions.filter.toggle,
        pastSentences: modifiedChartOptions.filter.pastSentences,
        threshold: modifiedChartOptions.filter.threshold,
      },
    }
  );

  chartMsg.window = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    modifiedChartOptions
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
        pastSentences: modifiedChartOptions.filter.pastSentences,
        threshold: modifiedChartOptions.filter.threshold,
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
});
process.once("SIGUSR2", function () {
  process.kill(process.pid, "SIGUSR2");
});
