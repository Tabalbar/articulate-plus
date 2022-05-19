module.exports = (header) => {
  for (let i = 0; i < covidColors.length; i++) {
    if (covidColors[i].header == header) {
      return covidColors[i].colors;
    }
  }
};

const covidColors = [
  {
    header: "region",
    colors: [
      "#ff0000",
      "#ff69c6",
      "#9400ff",
      "#0037ff",
      "#00fff8",
      "#00ff08",
      "#d5ff00",
    ],
  },
  {
    header: "area type",
    colors: ["#d5ff00", "#00ff08", "#0037ff", "#ff69c6", "#ff0000"],
  },
  {
    header: "elderly percentage",
    colors: ["#b30164", "#c74f81", "#d97d9f", "#e8a9be", "#f5d4de", "#121212"],
  },
  {
    header: "access to doctors",
    colors: ["#010ab3", "#5d3fc3", "#8c6dd3", "#b59ce3", "#dacdf1", "#121212"],
  },
  {
    header: "uninsured",
    colors: ["#01b369", "#59c386", "#88d3a3", "#b1e2c1", "#d8f1e0", "#121212"],
  },
  {
    header: "diabetes",
    colors: ["#6fb301", "#90c24a", "#aed279", "#cae1a5", "#e5f0d2", "#121212"],
  },
  {
    header: "cardiovascular disease",
    colors: ["#b38401", "#c79b44", "#d8b372", "#e7cca0", "#f4e5cf", "#121212"],
  },
  {
    header: "poverty",
    colors: ["#b30101", "#cb4c33", "#e07b62", "#efa794", "#fad3c8", "#121212"],
  },
  {
    header: "african american",
    colors: ["#017ab3", "#6499c6", "#9bbad9", "#cddcec", "#121212"],
  },
  {
    header: "Hispanic",
    colors: ["#01b33b", "#5bc363", "#89d38a", "#b2e2b0", "#d9f1d7", "#121212"],
  },
  {
    header: "covid risk",
    colors: ["#0800af", "#5e3bc0", "#8c6ad1", "#b59ae1", "#daccf0", "#121212"],
  },
  {
    header: "social vulnerability",
    colors: ["#b301b2", "#c652c2", "#d781d1", "#e6abe1", "#f3d5f0", "#121212"],
  },
];
