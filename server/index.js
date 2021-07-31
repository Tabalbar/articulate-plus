const express = require("express");
const PORT = process.env.PORT || 6000;
const app = express();
const path = require("path");
const ExtendNLP = require("./Pre-processing/ExtendNLP");

/**
 * This is for the Neural Network
 */
const { NlpManager } = require("node-nlp");

const manager = new NlpManager({
  languages: ["en"],
  forceNER: true,
  nlu: { log: false },
});

manager.addDocument(
  "en",
  "I want to see the comparison of nominal and quantitative",
  "bar"
);
manager.addDocument(
  "en",
  "show me a a comparison of nominal and quantitative",
  "bar"
);
manager.addDocument("en", "show me the distribution of nominal", "bar");
manager.addDocument(
  "en",
  "show me a graph with nominal nominal and quantitative",
  "bar"
);
manager.addDocument(
  "en",
  "show me the data for nominal nominal and quantitative",
  "bar"
);
manager.addDocument(
  "en",
  "show me a bar chart of nominal and quantitative",
  "bar"
);
manager.addAnswer("en", "bar", "bar");

manager.addDocument(
  "en",
  "I want to see the comparison of quantitative over time",
  "line"
);
manager.addDocument(
  "en",
  "show me the comparison of quantitative over temporal",
  "line"
);
manager.addDocument(
  "en",
  "Show me the temoral over the years of nominal and quantitative",
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
  "Show me the relationship of quantitative and quantitative",
  "scatter"
);
manager.addDocument(
  "en",
  "I want to see quantitative by quantitative",
  "scatter"
);
manager.addDocument("en", "show me quantiative by quantitative", "scatter");
manager.addDocument(
  "en",
  "show me a scatter plot of quantitative and quantitative",
  "scatter"
);
manager.addDocument(
  "en",
  "show me a point chart of quantitative and quantitative",
  "scatter"
);
manager.addDocument(
  "en",
  "show me a bubble chart of quantitative and quantitative colored by nominal",
  "scatter"
);
manager.addAnswer("en", "scatter", "scatter");

// manager.addDocument('en', 'show me the distribution of quantitative and quantitative', 'heatmap');
// manager.addDocument('en', 'show me a 2D heatmap', 'heatmap');
// manager.addAnswer('en', 'heatmap', 'heatmap');

manager.addDocument(
  "en",
  "I want to see the difference of nominal by quantitative quantitative and quantitative",
  "parallelCoordinates"
);
manager.addAnswer("en", "parallelCoordinates", "parallelCoordinates");

manager.addDocument("en", "show me a quantitative of nominal", "map");
manager.addAnswer("en", "map", "map");

// Train and save the model.
(async () => {
  await manager.train();
  manager.save();
})();
//***************** */

app.use(express.json({ limit: "500mb" }));
app.use(express.urlencoded({ extended: true, limit: "500mb" }));

app.use(express.static(path.resolve(__dirname, "../client/build")));

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
  let explicitChartType = getExplicitChartType(chartMsg.command);
  if (explicitChartType) {
    let options = {
      semanticAnalysis: false,
      window: {
        toggle: false,
        pastSentences: 20,
      },
      neuralNetwork: false,
    };
    chartMsg.explicitChart = createCharts(explicitChartType, chartMsg, options);
    // chartMsg.explicitChart = explicitChart(explicitChartType, chartMsg);
  } else {
    chartMsg.explicitChart = "";
  }
  console.log(chartMsg.explicitChart.charts);
  /**
   * Inferred implicit chart
   */
  const inferredResponse = await manager.process(
    "en",
    chartMsg.generalizedCommand
  );
  if (inferredResponse.intent !== "None") {
    let options = {
      semanticAnalysis: true,
      window: {
        toggle: true,
        pastSentences: 20,
      },
      neuralNetwork: true,
    };
    chartMsg.inferredChart = createCharts(
      inferredResponse.intent,
      chartMsg,
      options
    );
  } else {
    chartMsg.inferredChart = "";
  }
  /**
   * modified implicit chart
   */
  const modifiedResponse = await manager.process(
    "en",
    chartMsg.generalizedCommand
  );
  if (modifiedResponse.intent !== "None") {
    chartMsg.modifiedChart = createCharts(
      modifiedResponse.intent,
      chartMsg,
      modifiedChartOptions
    );
  } else {
    chartMsg.modifiedChart = "";
  }
  console.log(chartMsg.explicitChart);
  CompareCharts(chartMsg);
  chartMsg.headerFrequencyCount = countHeaderFrequency(
    chartMsg.transcript,
    chartMsg.featureMatrix,
    chartMsg.synonymMatrix,
    chartMsg.data,
    {
      semanticAnalysis: true,
      window: {
        toggle: true,
        pastSentences: 999,
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
