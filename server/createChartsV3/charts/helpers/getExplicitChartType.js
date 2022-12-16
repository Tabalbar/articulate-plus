/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
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
