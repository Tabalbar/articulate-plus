module.exports = (extractedHeaders, intent) => {
    const headerLength = extractedHeaders.length
    let headerTitles = [];
    for(let i = 0; i < extractedHeaders.length; i++) {
        let headers = extractedHeaders[i].split(" ")
        let title = ""
        for(let n = 0; n < headers.length; n++) {
            title += headers[n].charAt(0).toUpperCase() + headers[n].slice(1) + " "
        }
        headerTitles.push(title)
    }
    switch (headerLength) {
        case 1:
            switch (intent) {
                case "bar":
                    return "Histogram of " + headerTitles[0]
                case "line":
                    return "Line chart of " + headerTitles[0]
                case "scatter":
                    return "Scatter plot of " + extractedHeaders[0]
            }
        case 2:
            return intent.charAt(0).toUpperCase() + intent.slice(1) + 
            " Chart of " + headerTitles[1] + "vs. " + headerTitles[0]
        case 3:
            return intent.charAt(0).toUpperCase() + intent.slice(1) + 
            " Chart of " + headerTitles[1] + "vs. " + headerTitles[0] + "Colored by " + headerTitles[2]
        default:
            return ""
    }
}