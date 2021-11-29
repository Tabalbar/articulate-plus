import * as use from "@tensorflow-models/universal-sentence-encoder";
import "@tensorflow/tfjs-backend-webgl";
import * as tf from "@tensorflow/tfjs-core";
import nlp from "compromise";

let specialTypes = [{ header: "map", type: "map" }];

const findType = (header, data) => {
  let lowerCaseHeader = header.toLowerCase();
  for (let i = 0; i < specialTypes.length; i++) {
    if (header === specialTypes[i].header) {
      return specialTypes[i].type;
    }
  }
  if (
    lowerCaseHeader.includes("date") ||
    lowerCaseHeader.includes("year") ||
    lowerCaseHeader.includes("month") ||
    lowerCaseHeader.includes("day") ||
    lowerCaseHeader.includes("months") ||
    lowerCaseHeader.includes("dates")
  ) {
    return "temporal";
  } else if (isNaN(data[1][header])) {
    return "nominal";
  } else {
    return "quantitative";
  }
};
// if (
//   (command.includes("where") ||
//     command.includes("see") ||
//     command.includes("show") ||
//     command.includes("what") ||
//     command.includes("make") ||
//     command.includes("plot") ||
//     command.includes("change") ||
//     command.includes("create") ||
//     command.includes("filter") ||
//     ((command.includes("make") ||
//       command.includes("modify") ||
//       command.includes("pivot") ||
//       command.includes("change")) &&
//       (command.includes("these") ||
//         command.includes("this") ||
//         command.includes("those")))) &&
//   !mute &&
//   listening
// ) {
//   setListening(false);

//   createCharts(command);

//   setTimeout(() => {
//     setListening(true);
//   }, 8000);
// }
const sentences = [
  "Make a chart on nominal and nominal",
  "What does the nominal look like",
  "create a chart on nominal and nominal",
  "show me nominal",
  "Where is nominal the highest",
  "Filter the chart by nominal",

  "Where is nominal the highest",
  "Where is nominal the lowest",
  "Can you Change this chart by adding nominal",
  "Can you filter this chart by nominal",
  "modify this chart by nominal",
  "can you plot nominal",
  "Can you create a chart on nominal and nominal",
  "how do nominal in the nominal",

  "show me the quantitative over temporal",
  "what is the quantitative of nominal",
  "where is quantitative the highest",
  "Create a chart on quantitative",
  "modify this chart by quantitative",
  "add quantitative to this chart",
];

export default class Node_NLP {
  constructor() {}

  init = async () => {
    this.model = await use.load();
    this.embedding = await this.model.embed(sentences);
    console.log("created");
  };

  getScore = async (sentenceToCompare, chartMsg) => {
    let doc = nlp(sentenceToCompare);

    for (let i = 0; i < chartMsg.featureMatrix.length; i++) {
      for (let n = 0; n < chartMsg.featureMatrix[i].length; n++) {
        if (doc.match(chartMsg.featureMatrix[i][n])) {
          doc.replace(
            chartMsg.featureMatrix[i][n],
            findType(chartMsg.featureMatrix[i][0], chartMsg.data)
          );
        }
      }
    }
    for (let i = 0; i < chartMsg.synonymMatrix.length; i++) {
      for (let n = 0; n < chartMsg.synonymMatrix[i].length; n++) {
        if (doc.match(chartMsg.synonymMatrix[i][n])) {
          doc.replace(
            chartMsg.synonymMatrix[i][n],
            findType(chartMsg.synonymMatrix[i][0], chartMsg.data)
          );
        }
      }
    }

    sentenceToCompare = doc.text();
    console.log(sentenceToCompare);
    const sentenceToComapreEmbedding = await this.model.embed(
      sentenceToCompare
    );
    const b = tf.slice(sentenceToComapreEmbedding, [0, 0], [1]);

    for (let i = 0; i < sentences.length; i++) {
      const a = tf.slice(this.embedding, [i, 0], [1]);
      const score = tf.matMul(a, b, false, true).dataSync();
      console.log(score);
      console.log(score[0] > 0.5);
      if (score[0] > 0.5) {
        return true;
      }
    }
    return false;
    // console.log(score);
  };

  // async init() {
  //   this.model = await use.load();
  //   this.embeddings = await model.embed(sentences);
  // }
}
// const model = await use.load();
// const embeddings = await model.embed(sentences);

// export default async function node_nlp(sentenceToCompare) {
//   //   const model = await use.load();
//   // const embeddings = await model.embed(sentences);

//   //   console.log(embeddings);
//   let sentenceOne = "Make a chart on var and var";
//   let sentenceTwo =
//     "I wonder what the weather will look like tomorrow when i show me a chart on var";

//   //   const testEmbeddingOne = await model.embed(sentenceOne);
//   //   const testEmbeddingTwo = await model.embed(sentenceTwo);
//   const testEmbeddingThree = await model.embed(sentenceToCompare);
//   for (let i = 0; i < sentences.length; i++) {
//     const a = tf.slice(embeddings, [i, 0], [1]);
//     // const embeddingOne = tf.slice(testEmbeddingOne, [0, 0], [1]);
//     // const embeddingTwo = tf.slice(testEmbeddingTwo, [0, 0], [1]);
//     const embeddingThree = tf.slice(testEmbeddingThree, [0, 0], [1]);
//     // const scoreOne = tf.matMul(a, embeddingOne, false, true).dataSync();
//     // const scoreTwo = tf.matMul(a, embeddingTwo, false, true).dataSync();
//     const scoreThree = tf.matMul(a, embeddingThree, false, true).dataSync();
//     // console.log(scoreOne, scoreTwo);
//     console.log(scoreThree);
//   }
// }
