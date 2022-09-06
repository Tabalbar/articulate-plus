/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const nlp = require("compromise");
nlp.extend(require("compromise-numbers"));
nlp.extend(require("compromise-dates"));
const findType = require("./createChartsV3/charts/helpers/findType");

module.exports = (command, attributes, data, featureMatrix, synonymMatrix) => {
  let doc = nlp(command);
  // const {featureMatrix, synonymMatrix} = createMatrixForAll(attributes, data)
  for (let i = 0; i < attributes.length; i++) {
    if (doc.match(attributes[i])) {
      doc.replace(attributes[i], findType(attributes[i], data));
    }
  }
  for (let i = 0; i < featureMatrix.length; i++) {
    for (let n = 0; n < featureMatrix[i].length; n++) {
      if (doc.match(featureMatrix[i][n])) {
        doc.replace(featureMatrix[i][n], findType(featureMatrix[i][0], data));
      }
    }
  }
  doc.numbers().replaceWith("quantitative");
  doc.dates().replaceWith("temporal");

  generalizedCommand = doc.text();
  return { generalizedCommand };
};
