const express = require("express");
const PORT = process.env.PORT || 6000;
const app = express();
const path = require('path');

const ExtendNLP = require('./Pre-processing/ExtendNLP')

/**
 * This is for the Neural Network
 */
const { NlpManager } = require('node-nlp');

const manager = new NlpManager({ languages: ['en'], forceNER: true });

manager.addDocument('en', 'I want to see the comparison of nominal and quantitative', 'bar');
manager.addDocument('en', 'show me a a comparison of nominal and quantitative', 'bar');
manager.addDocument('en', 'show me the distribution of nominal', 'bar');
manager.addDocument('en', 'show me a graph with nominal nominal and quantitative', 'bar');
manager.addDocument('en', 'show me the data for nominal nominal and quantitative', 'bar');
manager.addAnswer('en', 'bar', 'bar');

manager.addDocument('en', 'I want to see the comparison of quantitative over time', 'line');
manager.addDocument('en', 'show me the comparison of quantitative over temporal', 'line');
manager.addDocument('en', 'Show me the temoral over the years of nominal and quantitative', 'line');
manager.addAnswer('en', 'line', 'line');

manager.addDocument('en', 'Show me the relationship of quantitative and quantitative', 'scatter');
manager.addDocument('en', 'I want to see quantitative by quantitative', 'scatter');
manager.addDocument('en', 'show me quantiative by quantitative', 'scatter');
manager.addAnswer('en', 'scatter', 'scatter');

manager.addDocument('en', 'show me the distribution of quantitative and quantitative', 'heatmap');
manager.addDocument('en', 'show me a 2D heatmap', 'heatmap');
manager.addAnswer('en', 'heatmap', 'heatmap');

manager.addDocument('en', 'I want to see the difference of nominal by quantitative quantitative and quantitative', 'parallelCoordinates');
manager.addAnswer('en', 'parallelCoordinates', 'parallelCoordinates');

// Train and save the model.
(async () => {
  await manager.train();
  manager.save();
})();
//***************** */


app.use(express.json({ limit: '50mb' }))
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

app.use(express.static(path.resolve(__dirname, '../client/build')));

/**
 * Initialize 
 */
app.post("/initialize", (req, res) => {
  // console.log(req.body)
  const { featureMatrix, synonymMatrix } = ExtendNLP(req.body.attributes, req.body.data)
  if (featureMatrix === null || synonymMatrix === null) {
    console.log("Error in pre-processing")
    res.status(405).send("Error in pre-processing")
  }
  res.json({ featureMatrix: featureMatrix, synonymMatrix: synonymMatrix });
});


/**
 * Generalize the command and send through chartMaker pipeline
 */
const normalizeCommand = require('./chartMaker/normalizeCommand')
const generalizeCommand = require('./chartMaker/generalizeCommand')
const chartMaker = require("./chartMaker/chartMaker")
const getExplicitChartType = require('./chartMaker/specifications/ExplicitChart')
const explicitChart = require('./chartMaker/explicit/explicitChart')

app.post("/createCharts", async (req, res) => {
  let chartMsg = req.body.chartMsg
  const normalizedCommand = normalizeCommand("show me a bar chart of monkeys")
  const { generalizedCommand, synonymCommand } = generalizeCommand(normalizedCommand, chartMsg.attributes,
    chartMsg.data, chartMsg.featureMatrix, chartMsg.synonymMatrix)
  /**
  * Getting ExplicitChart
  */
  let explicitChartType = getExplicitChartType(normalizedCommand)
  if (explicitChartType) {
    chartMsg.explicitChart = explicitChart(explicitChartType, chartMsg)
  } else {
    chartMsg.explicitChart = null
  }

  /**
   * Inferred implicit chart
   */
  // const response = await manager.process('en', generalizedCommand)
  // console.log(response.intent !== "none")
  // if (response.intent) {
  //   // chartMsg.frequencyChart = frequencyChart(chartMsg, response.intent)
  // } else {
  //   chartMsg.frequencyChart = null
  // }


  console.log(chartMsg.explicitChart)
  res.send({ chartMsg })
});
// All other GET requests not handled before will return our React app
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../client/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`);
});
