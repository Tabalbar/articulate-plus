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

manager.addDocument("en", "show me the distribution of nominal", "bar");
manager.addDocument("en", "show me a graph with nominal and nominal", "bar");
manager.addDocument("en", "show me a chart of nominal and nominal", "bar");
manager.addAnswer("en", "bar", "bar");

manager.addDocument(
  "en",
  "I want to see the comparison of nominal over time",
  "line"
);
manager.addDocument("en", "show me nominal by date", "line");
manager.addDocument(
  "en",
  "show me the comparison of nominal over temporal",
  "line"
);
manager.addDocument(
  "en",
  "Show me the temporal over the year of nominal and quantitative",
  "line"
);
manager.addDocument(
  "en",
  "show me a line chart of nominal and quantitative",
  "line"
);
manager.addAnswer("en", "line", "line");

manager.addDocument(
  "en",
  "I want to see quantitative by quantitative",
  "scatter"
);
manager.addDocument(
  "en",
  "show me the relationship of quantitative and quantitative",
  "scatter"
);
manager.addDocument(
  "en",
  "what is the quantitative of quantitative",
  "scatter"
);
manager.addAnswer("en", "scatter", "scatter");

manager.addDocument(
  "en",
  "show me the correlation of quantiative and quantitative",
  "heatmap"
);
manager.addDocument("en", "show me quantitative by quantitative", "heatmap");
manager.addAnswer("en", "heatmap", "heatmap");
// case "bar":
//   delete chartObj.charts.spec.mark
//   layerMark = "bar"
//   return chartObj, layerMark;
// case "line":
//   delete chartObj.charts.spec.mark
//   layerMark = "line"
//   return chartObj, layerMark
// case "scatter":
//   delete chartObj.charts.spec.mark
//   layerMark = "point"
//   return chartObj, layerMark
// case "pie":
//   delete chartObj.charts.spec.mark
//   layerMark = "arc"
//   return chartObj, layerMark
// case "marginalHistogram":
//   delete chartObj.charts.spec.mark
//   return chartObj
// case "heatmap":
//   delete chartObj.charts.spec.mark
//   layerMark = "rect"
//   return chartObj, layerMark
// case "lineArea":
//   layerMark = "area"
//   return chartObj, layerMark
// case "stackedBar":
//   layerMark = "bar"
//   return chartObj, layerMark
// case "normalizedStackedBar":
//   layerMark = "bar"
//   return chartObj, layerMark
// case "normalizedLineArea":
//   layerMark = "area"

//   return chartObj, layerMark
// // case "candleStick":
// //     chartObj.charts.spec.mark = "bar"
// //     return chartObj
// case "parallelCoordinates":
//   chartObj.charts.spec.mark = "line"
//   return chartObj

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
const getExplicitChartType = require("./createCharts/explicit/ExplicitChart");
const CompareCharts = require("./CompareCharts");
const countHeaderFrequency = require("./createCharts/countHeaderFrequency");

const createCharts = require("./createCharts/createCharts");
const ChartInfo = require("../newCreateCharts/chartObj/ChartInfo");

const explicitChart = require("./oldChartMaker/explicit/explicitChart");
const inferredChart = require("./oldChartMaker/inferred/inferredChart");
const modifiedChart = require("./oldChartMaker/modified/modifiedChart");

app.post("/createCharts", async (req, res) => {
  let chartMsg = req.body.chartMsg;
  let modifiedChartOptions = req.body.modifiedChartOptions;
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
  // const chartObj = new ChartInfo(chartMsg, modifiedChartOptions, intent);
  // let testing = chartObj.extractHeaders();
  // let testing2 = chartObj.extractFilteredHeaders();
  // console.log(testing, testing2);
  if (!intent) {
    intent = (await manager.process("en", chartMsg.generalizedCommand)).intent;
  }
  if (intent !== "None") {
    /**
     * Explicit Chart
     */
    chartMsg.explicitChart = explicitChart(intent, chartMsg);

    /**
     * Window + Sentiment Chart
     */
    chartMsg.inferredChart = inferredChart(intent, chartMsg);

    /**
     * modified implicit chart
     */

    chartMsg.modifiedChart = modifiedChart(
      intent,
      chartMsg,
      modifiedChartOptions
    );

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
