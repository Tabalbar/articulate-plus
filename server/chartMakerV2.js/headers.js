module.exports = {
    extractHeaders: (command, headers, data, intent) => {
        /**
           * Extract attributes mentioned in command
           */
        let extractedHeaders = []
        for (let i = 0; i < headers.length; i++) {
            if (command.includes(headers[i].toLowerCase()) || command.includes(headers[i].toLowerCase())) {
                extractedHeaders.push(headers[i])
            }
        }

        /**
         * For COVID-19 data
         * Find the map attirbute for map intent
         */
        if (intent === "map") {
            let mapFound = false;
            for (let i = 0; i < extractedHeaders.length; i++) {
                if (extractedHeaders[i] == "map") {
                    mapFound = true;
                }
            }
            if (!mapFound) {
                for (let i = 0; i < headers.length; i++) {
                    if (headers[i] == "map") {
                        extractedHeaders.push(headers[i])
                    }
                }
            }
        }

        /**
         * Find Temporal attribute
         */
        if (command.includes("overtime") || command.includes("time")) {
            let foundTime = false
            for (let i = 0; i < extractedHeaders.length; i++) {
                if (findType(extractedHeaders[i], data) === "temporal") {
                    foundTime = true
                    break
                }
            }
            if (!foundTime) {
                for (let i = 0; i < headers.length; i++) {
                    if (findType(headers[i], data) === "temporal") {
                        extractedHeaders.push(headers[i])
                        break;
                    }
                }
            }
        }
        return extractedHeaders;
    },
    extractFilteredData: () => {
        let doc = nlp(command)
        let extractedFilteredHeaders = []
        let foundTimeHeader = false
        doc.nouns().toSingular()

        //Extract data from command
        for (let i = 0; i < uniqueNominalData.length; i++) {
            extractedFilteredHeaders[uniqueNominalData[i][0]] = []
            for (let n = 1; n < uniqueNominalData[i].length; n++) {
                if (doc.has(uniqueNominalData[i][n])) {
                    extractedFilteredHeaders[uniqueNominalData[i][0]].push(uniqueNominalData[i][n])
                }

            }

            //If the header is temporal type, find if dates are in the command
            if (findType(uniqueNominalData[i][0], data) === "temporal" && !foundTimeHeader) {
                const { foundTime, timeHeader } = extractHeadersWithoutFilter(doc, headers, data, command)
                if (!foundTime) {
                    findDates(doc, extractedFilteredHeaders[uniqueNominalData[i][0]])
                    command += " " + uniqueNominalData[i][0]
                    foundTimeHeader = true;

                } else {
                    if (timeHeader === uniqueNominalData[i][0]) {
                        findDates(doc, extractedFilteredHeaders[uniqueNominalData[i][0]])

                    }


                }


            }

        }
        //function used to find dates.
        function findDates(docCommand, header) {
            if (docCommand.match("to") || docCommand.match("through") || docCommand.match("and")) {

                //Finds the word "to" and tries to find dates before and after
                let termsBefore = docCommand.before('to').terms().out('array')
                let termsAfter = docCommand.after('to').terms().out('array')
                const yearBefore = termsBefore[termsBefore.length - 1]
                const yearAfter = termsAfter[0]
                if (!isNaN(yearBefore) && !isNaN(yearAfter)) {
                    header.push(yearBefore)
                    header.push(yearAfter)

                }

            }
        }

        //if dates were mentioned in the command but no data attribute. 
        //Find first instance of date attribute in the data
        function extractHeadersWithoutFilter(docCommand, headers, data) {
            let foundTime = false
            let index;
            for (let i = 0; i < headers.length; i++) {

                if (docCommand.has(headers[i]) && findType(headers[i], data) === "temporal") {
                    index = i;
                    foundTime = true
                    break;
                }
            }
            let timeHeader = headers[index]
            return { foundTime, timeHeader }
        }
        return extractedFilteredHeaders;
    }
}

