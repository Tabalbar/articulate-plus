module.exports = (extractedHeaders, targetIndex, sourceIndex) => {
  let tmpHeader = extractedHeaders[targetIndex];
  extractedHeaders[targetIndex] = extractedHeaders[sourceIndex];
  extractedHeaders[sourceIndex] = tmpHeader;
  return extractedHeaders;
};
