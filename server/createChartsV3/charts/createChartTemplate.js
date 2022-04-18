module.exports = (chartMsg, headerFrequencyCount, filterFrequencyCount) => {
  //Create delta time to check when chart was made compared to beginning
  //of th session
  let time = (new Date() - new Date(chartMsg.deltaTime)) / 1000 / 60;
  time = Math.round(time * 100) / 100;
  let chart = {
    id: 0,
    title: "",
    width: 400,
    height: 220,
    mark: "",
    transform: [],
    encoding: {
      column: {},
      y: {},
      x: {},
    },
    initialized: createDate(),
    timeChosen: [],
    timeClosed: [],
    deltaTime: time,
    timeSpentHovered: 0,
    data: { name: "table" },
    command: chartMsg.command,
    pivotThis: false,
    numClicks: 0,
    headerFrequencyCount: headerFrequencyCount,
    filterFrequencyCount: filterFrequencyCount,
    fetchedURL: false,
  };
  return chart;
};

function createDate() {
  let date = new Date();
  const [month, day, year] = [
    date.getMonth(),
    date.getDate(),
    date.getFullYear(),
  ];
  let [hour, minutes, seconds] = [
    date.getHours(),
    date.getMinutes(),
    date.getSeconds(),
  ];
  let amOrPm = "AM";
  if (hour >= 12) {
    hour = hour - 12;
    amOrPm = "PM";
  }
  if (hour == 0) {
    hour = 12;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  date = hour + ":" + minutes + ":" + seconds + " " + amOrPm;
  return date;
}
