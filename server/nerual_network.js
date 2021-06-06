const { NlpManager } = require('node-nlp')



module.exports =  function nerual_network() {


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

    manager.addDocument('en', 'show me the composition of quantitative', 'pie');
    manager.addDocument('en', 'I want to see the quantitative and nominal', 'pie');
    manager.addDocument('en', 'show me the percentage of quantitative and nominal', 'pie');
    manager.addAnswer('en', 'pie', 'pie');

    manager.addDocument('en', 'can you show me a marginal heat map', 'marginalHistogram');
    manager.addDocument('en', 'I want to see the distribution of quantitative and quantitative', 'marginalHistogram');
    manager.addDocument('en', 'show me a graph with extra bars on the side', 'marginalHistogram');
    manager.addDocument('en', 'show me a heat map of quantitative and quantitative with bar charts on the side', 'marginalHistogram');
    manager.addAnswer('en', 'marginalHistogram', 'marginalHistogram');

    manager.addDocument('en', 'show me the distribution of quantitative and quantitative', 'heatmap');
    manager.addDocument('en', 'show me a 2D heatmap', 'heatmap');
    manager.addAnswer('en', 'heatmap', 'heatmap');

    manager.addDocument('en', 'Show me the area under the curve for temporal quantitative and temoral', 'lineArea');
    manager.addDocument('en', 'show me the quantitative and nominal over time', 'lineArea');
    manager.addAnswer('en', 'lineArea', 'lineArea');

    // manager.addDocument('en', 'show me a normalized graph with quantitative and nominal over time', 'normalizedLineArea');
    // manager.addDocument('en', 'show me a normalized of temporal quantitative and nominal ', 'normalizedLineArea');
    // manager.addAnswer('en', 'normalizedLineArea', 'normalizedLineArea');

    manager.addDocument('en', 'show me a stacked bar', 'stackedBar');
    manager.addAnswer('en', 'stackedBar', 'stackedBar');

    // manager.addDocument('en', 'show me a normalized stacked bar chart of ', 'normalizedStackedBar');
    // manager.addDocument('en', 'show me a normalized stacked bar chart of temporal quantitative and nominal', 'normalizedStackedBar');
    // manager.addAnswer('en', 'normalizedStackedBar', 'normalizedStackedBar');

    // manager.addDocument('en', 'show me the stock trend', 'candleStick');
    // manager.addAnswer('en', 'candleStick', 'candleStick');

    manager.addDocument('en', 'I want to see the difference of nominal by quantitative quantitative and quantitative', 'parallelCoordinates');
    manager.addAnswer('en', 'parallelCoordinates', 'parallelCoordinates');

    manager.addDocument('en', 'show me a radar graph of temporal and quantitative', 'radar');
    manager.addAnswer('en', 'radar', 'radar');

    // manager.addDocument('en', 'this but with ', 'filter');
    // manager.addAnswer('en', 'filter', 'filter');

    // Train and save the model.
    (async () => {
        await manager.train();
        manager.save();
        const response = await manager.process('en', 'I should go now');
    })();

}