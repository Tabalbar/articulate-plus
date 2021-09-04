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

manager.addDocument("en", "show me a map of nominal", "map");
manager.addDocument("en", "show me where nominal", "map");

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
      sentimentAnalysis: false,
      window: {
        toggle: false,
        pastSentences: 20,
      },
      neuralNetwork: false,
      useSynonyms: false,
    };
    chartMsg.explicitChart = createCharts(explicitChartType, chartMsg, options);
    // chartMsg.explicitChart = explicitChart(explicitChartType, chartMsg);
  } else {
    const explicitResponse = await manager.process(
      "en",
      chartMsg.generalizedCommand
    );
    if (explicitResponse.intent !== "None") {
      let options = {
        sentimentAnalysis: false,
        window: {
          toggle: false,
          pastSentences: 20,
        },
        neuralNetwork: false,
        useSynonyms: false,
      };
      chartMsg.explicitChart = createCharts(
        explicitResponse.intent,
        chartMsg,
        options
      );
    } else {
      chartMsg.explicitChart = "";
    }
  }

  /**
   * Window & Sentiment call
   */
  const windowSentimentResponse = await manager.process(
    "en",
    chartMsg.generalizedCommand
  );
  if (windowSentimentResponse.intent !== "None") {
    let options = {
      sentimentAnalysis: true,
      window: {
        toggle: true,
        pastSentences: modifiedChartOptions.window.pastSentences,
      },
      neuralNetwork: true,
      useSynonyms: modifiedChartOptions.useSynonyms,
    };
    chartMsg.inferredChart = createCharts(
      windowSentimentResponse.intent,
      chartMsg,
      options
    );
  } else {
    chartMsg.inferredChart = "";
  }

  /**
   * modified implicit chart
   */
  const windowResponse = await manager.process(
    "en",
    chartMsg.generalizedCommand
  );
  if (windowResponse.intent !== "None") {
    chartMsg.modifiedChart = createCharts(
      windowResponse.intent,
      chartMsg,
      modifiedChartOptions
    );
  } else {
    chartMsg.modifiedChart = "";
  }
  CompareCharts(chartMsg);
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
