const { default: createDate } = require("./helpers/createDate");
// const [chartMsg, setChartMsg] = useState(
//     JSON.parse(localStorage.getItem("chartMsg")) || {
//       command: "", //Query
//       attributes: [],
//       data: "",
//       transcript: "",
//       uncontrolledTranscript: "",
//       loggedTranscript: [], // {sentence: string, date: createDate()}
//       loggedUncontrolledTranscript: [],
//       synonymMatrix: [], //Synonyms used in attributes
//       featureMatrix: [], //Unique data values
//       currentCharts: [],
//       explicitChart: [],
//       inferredChart: [],
//       modifiedChart: [],
//       assistantResponse: "",
//       errMsg: [],
//       charts: [],
//   window_sentiment: {
//     quantitative: [],
//     nominal: [],
//     temporal: [],
//     map: [],
//   },
//   window: {
//     quantitative: [],
//     nominal: [],
//     temporal: [],
//     map: [],
//   },
//   total: {
//     quantitative: [],
//     nominal: [],
//     temporal: [],
//     map: [],
//   },
//     }
//   );
export default class ChartObj {
  static command = "";
  static transcript = "";
  static uncontrolledTranscript = "";
  static loggedTranscript = [];
  static loggedUncontrolledTranscript = [];
  static explicitChart = [];
  static windowSentimentChart = [];
  static windowChart = [];
  static charts = [];
  static window_sentiment = {
    quantitative: [],
    nominal: [],
    temporal: [],
    map: [],
  };
  static window = {
    quantitative: [],
    nominal: [],
    temporal: [],
    map: [],
  };
  static total = {
    quantitative: [],
    nominal: [],
    temporal: [],
    map: [],
  };

  constructor(data, attributes, synonymMatrix, featureMatrix, options) {
    this.data = data;
    this.attributes = attributes;
    this.synonymMatrix = synonymMatrix;
    this.featureMatrix = featureMatrix;
    this.options = options;
  }

  static addToTranscripts(sentence) {
    if (this.transcript !== "") {
      this.transcript += ". " + sentence;
      this.loggedTranscript.push({ sentence: sentence, date: createDate() });
    } else {
      this.transcript = sentence;
      this.loggedTranscript.push({ sentence: sentence, date: createDate() });
    }
  }

  static async serverRequest(setVoiceMsg) {
    const response = await fetch("/createCharts", {
      method: "POST",
      body: JSON.stringify({
        chartMsg: this,
        modifiedChartOptions: this.options,
      }),
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });
    // decrypt message from server
    const body = await response.text();
    const responseChartMsg = JSON.parse(body);

    //tmp var to hold charts
    let tmpChartMsg = responseChartMsg.chartMsg;
    //Must add explicit first
    let newCharts = [
      ...tmpChartMsg.explicitChart,
      ...tmpChartMsg.inferredChart,
      ...tmpChartMsg.modifiedChart,
    ];
    //Clean up for charts that weren't generated
    newCharts = newCharts.filter((x) => {
      return x !== "";
    });

    this.charts = [...this.charts, ...newCharts];
    this.window_sentiment = tmpChartMsg.window_sentiment;
    this.window = tmpChartMsg.window;
    this.total = tmpChartMsg.total;

    // How many charts were generated
    let count = newCharts.length;
    let assistantResponse;

    if (count == 0) {
      assistantResponse = "I couldn't find any charts for you";
    } else if (count == 1) {
      assistantResponse = "I have " + count.toString() + " chart for you.";
    } else {
      assistantResponse = "I have " + count.toString() + " charts for you.";
    }
    //Voice syntheiszer
    setVoiceMsg(assistantResponse);
  }
}
