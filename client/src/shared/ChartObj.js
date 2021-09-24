import XLSX from "xlsx";
const { default: createDate } = require("../helpers/createDate");

export default class ChartObj {
  static command = "asdf";
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
  static data = [];
  static attributes = [];
  static synonymMatrix = [];
  static featureMatrix = [];
  static options = [];
  wasInitialized = false;

  constructor() {
    //   const { synonymMatrix, featureMatrix, headers, list } = loadData(csv);
    //   this.data = list;
    //   this.attributes = headers;
    //   this.synonymMatrix = synonymMatrix;
    //   this.featureMatrix = featureMatrix;
    //   // this.options = options;
  }
  static initialize() {
    if (this.wasInitialized) {
      return this;
    } else {
      this.wasInitialized = true;

      return this;
    }
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
  static async loadData(e) {
    return new Promise((resolve) => {
      e.preventDefault();
      const file = e.target.files[0];
      var reader = new FileReader();
      reader.onload = async (e) => {
        // Use reader.result
        const bstr = e.target.result;
        const wb = XLSX.read(bstr, { type: "binary" });
        /* Get first worksheet */
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        /* Convert array of arrays */
        const data = XLSX.utils.sheet_to_csv(ws, { header: 1 });
        const dataStringLines = data.split(/\r\n|\n/);
        const headers = dataStringLines[0].split(
          /,(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)/
        );

        const list = [];
        for (let i = 1; i < dataStringLines.length; i++) {
          const row = dataStringLines[i].split(
            /,(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)/
          );
          if (headers && row.length == headers.length) {
            const obj = {};
            for (let j = 0; j < headers.length; j++) {
              let d = row[j];
              if (d.length > 0) {
                if (d[0] == '"') d = d.substring(1, d.length - 1);
                if (d[d.length - 1] == '"') d = d.substring(d.length - 2, 1);
              }
              if (headers[j]) {
                obj[headers[j]] = d;
              }
            }

            if (Object.values(obj).filter((x) => x).length > 0) {
              list.push(obj);
            }
          }
        }

        let tmpDataHead = [];
        for (let i = 0; i < 100; i++) {
          tmpDataHead.push(list[i]);
        }
        const response = await fetch("/initialize", {
          method: "POST",
          body: JSON.stringify({ attributes: headers, data: list }),
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        });
        const body = await response.text();
        const { synonymMatrix, featureMatrix } = JSON.parse(body);
        this.synonymMatrix = synonymMatrix;
        this.featureMatrix = featureMatrix;
        this.attributes = headers;
        this.data = list;
        return resolve({ synonymMatrix, featureMatrix, headers, list });
      };
      reader.readAsBinaryString(file);
    });
  }

  static async serverRequest(setVoiceMsg) {
    return Promise(async (resolve) => {
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
      return resolve();
    });
  }
}

// async function
