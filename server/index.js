const express = require("express");
const PORT = process.env.PORT || 6000;
const app = express();
const path = require('path');

//Set up Neural Network for queries
const neural_network = require("./nerual_network")
neural_network()

// Have Node serve the files for our built React app
app.use(express.static(path.resolve(__dirname, '../client/build')));

app.post("/api", (req, res) => {
    nlp.extend((Doc, world) => {
        // add methods to run after the tagger
        const nlpHeaders = req.body.headers
    
        world.postProcess(doc => {
          nlpHeaders.forEach(header => {
            doc.match(header).tag('#Noun')
          });
        })
      })
  res.json({ message: "Hello from server!" });
});

// All other GET requests not handled before will return our React app
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../client/build', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server listening on ${PORT}`);
});
