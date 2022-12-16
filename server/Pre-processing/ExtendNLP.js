/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const nlp = require("compromise");
const createMatrixForAll = require("./createMatrixForAll");

module.exports = (headers, data) => {
  nlp.extend((Doc, world) => {
    // add methods to run after the tagger

    world.postProcess((doc) => {
      headers.forEach((header) => {
        doc.match(header).tag("#Noun");
        doc.match(header + "s").tag("#Noun");
      });
    });
  });
  const { featureMatrix, synonymMatrix } = createMatrixForAll(headers, data);
  return { featureMatrix, synonymMatrix };
};
