module.exports = (header, data) => {
    let lowerCaseHeader = header.toLowerCase()
    if (lowerCaseHeader.includes('date')
        || lowerCaseHeader.includes('year') || lowerCaseHeader.includes('month')
        || lowerCaseHeader.includes('day') || lowerCaseHeader.includes('months')
        || lowerCaseHeader.includes('dates')) {
        return "temporal"
    } else if (isNaN(data[1][header])) {
        return "nominal"
    } else {
        return "quantitative"
    }
}