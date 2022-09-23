/**
 * Copyright (c) University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
const nlp = require("compromise");

module.exports = (header, data) => {
  let unique = [...new Set(data.map((item) => item[header]))];

  if (header == "access_to_doctor") {
    unique = [...new Set(data.map((item) => item["access_to_doctors"]))];
  }
  if (header == "date") {
    return false;
  }
  console.log(unique);
  if (unique.length == 5 || unique.length == 6) {
    for (let i = 0; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (
        doc.has("very high") ||
        doc.has("very-high") ||
        unique[i].includes("very-high")
      ) {
        switchHeaders(unique, 0, i);
        break;
      }
    }

    for (let i = 1; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("high") || unique[i].includes("high")) {
        switchHeaders(unique, 1, i);
        break;
      }
    }

    for (let i = 2; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (
        doc.has("moderate") ||
        doc.has("medium") ||
        unique[i].includes("medium") ||
        unique[i].includes("moderate")
      ) {
        switchHeaders(unique, 2, i);
        break;
      }
    }

    for (let i = 3; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("low") || unique[i].includes("low")) {
        switchHeaders(unique, 3, i);
        break;
      }
    }

    for (let i = 0; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (
        doc.has("very low") ||
        doc.has("very-low") ||
        unique[i].includes("very-low")
      ) {
        switchHeaders(unique, 4, i);
        break;
      }
    }
  }
  if (unique.length == 4) {
    for (let i = 0; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("high")) {
        switchHeaders(unique, 0, i);
        break;
      }
    }

    for (let i = 1; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("moderate") || doc.has("medium")) {
        switchHeaders(unique, 1, i);
        break;
      }
    }

    for (let i = 2; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("low")) {
        switchHeaders(unique, 2, i);
        break;
      }
    }

    for (let i = 3; i < unique.length; i++) {
      let doc = nlp(unique[i]);
      if (doc.has("very low")) {
        switchHeaders(unique, 3, i);
        break;
      }
    }
  }
  return unique;
};

function switchHeaders(extractedHeaders, targetIndex, sourceIndex) {
  let tmpHeader = extractedHeaders[targetIndex];
  extractedHeaders[targetIndex] = extractedHeaders[sourceIndex];
  extractedHeaders[sourceIndex] = tmpHeader;
  return extractedHeaders;
}
