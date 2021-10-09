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
