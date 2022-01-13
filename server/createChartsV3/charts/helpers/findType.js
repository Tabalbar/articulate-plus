let specialTypes = [
  { header: "map", type: "map" },
  { header: "lat", type: "lat" },
  { header: "long", type: "long" },
];

module.exports = (header, data) => {
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
