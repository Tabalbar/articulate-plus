const switchHeaders = require("./switchHeaders");

module.exports = (chartMsg, extractedHeaders) => {
  let locationFound = false;
  let latLong = false;
  let fips = false;
  for (let i = 0; i < extractedHeaders.length; i++) {
    if (
      extractedHeaders[i].toLowerCase().includes("lat") ||
      extractedHeaders[i].toLowerCase().includes("latitude")
    ) {
      locationFound = true;
      latLong = true;
      break;
    }
    if (extractedHeaders[i].toLowerCase().includes("map")) {
      locationFound = true;
      fips = true;
      break;
    }
  }
  if (!locationFound) {
    for (let i = 0; i < chartMsg.attributes.length; i++) {
      if (
        chartMsg.attributes[i].toLowerCase().includes("lat") ||
        chartMsg.attributes[i].toLowerCase().includes("latitude")
      ) {
        extractedHeaders.push(chartMsg.attributes[i]);
      }
      if (
        chartMsg.attributes[i].toLowerCase().includes("long") ||
        chartMsg.attributes[i].toLowerCase().includes("longitude")
      ) {
        extractedHeaders.push(chartMsg.attributes[i]);
      }
      if (chartMsg.attributes[i].toLowerCase().includes("map")) {
        extractedHeaders.push(chartMsg.attributes[i]);
      }
    }
  }

  if (locationFound) {
    if (latLong) {
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (
          extractedHeaders[i].toLowerCase().includes("long") ||
          extractedHeaders[i].toLowerCase().includes("longitude")
        ) {
          switchHeaders(extractedHeaders, 1, i);
          break;
        }
      }
      for (let i = 0; i < extractedHeaders.length; i++) {
        if (
          extractedHeaders[i].toLowerCase().includes("lat") ||
          extractedHeaders[i].toLowerCase().includes("latitude")
        ) {
          switchHeaders(extractedHeaders, 1, i);
          break;
        }
      }
    }
  }
  if (fips) {
    for (let i = 0; i < extractedHeaders.length; i++) {
      if (extractedHeaders[i].toLowerCase().includes("map")) {
        switchHeaders(extractedHeaders, 0, i);
        break;
      }
    }
  }
};
