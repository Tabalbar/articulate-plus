const nlp = require("compromise");
const chartOptions = require("./chartOptions");
module.exports = (command, availableCharts) => {
  let doc = nlp(command);
  for (let i = 0; i < availableCharts.length; i++) {
    if (doc.has(availableCharts[i].key) && availableCharts[i].available) {
      return availableCharts[i].mark;
    }
  }
  return false;
};
