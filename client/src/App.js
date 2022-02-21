import React, { useState, useEffect, useRef } from "react";
import "semantic-ui-css/semantic.min.css";

//Pages
import Diagnostics from "./pages/Diagnostics";
import Charts from "./pages/Charts";

//Components
import Dictaphone from "./components/voice/Dictaphone";
import ArtyContainer from "./components/staticWindows/ArtyContainer";

//Helper functions
import { serverRequest } from "./helpers/serverRequest";
import createDate from "./helpers/createDate";

import { ChakraProvider, Button, Box, Input } from "@chakra-ui/react";

//For computer talking
import listeningImage from "./images/idle-small.gif";
import talkingImage from "./images/talking-small.gif";
import muteImage from "./images/mute-small.gif";
import thinkingImage from "./images/thinking-small.gif";
import { thinking } from "./components/voice/assistantVoiceOptions";
import AttributeContainer from "./components/staticWindows/AttributeContainer";
import useInterval from "./helpers/useInterval";
import chartSound from "./sounds/chartSound.wav";

import { commandChecker } from "./helpers/commandChecker";
import speakVoice from "./components/voice/speakVoice";

function App() {
  //Start Dictaphone to start listening
  const [startStudy, setStartStudy] = useState(false);

  const [, setForceUpdate] = useState(true);

  //Mute for synthesizer
  const [mute, setMute] = useState(false);

  // State for dashboard or diagnostics page
  const [chartsPage, setChartsPage] = useState(true);

  //Charts held in Chosen component
  const [charts, setCharts] = useState([]);

  const [chartToHighlight, setChartToHighlight] = useState(null);

  //Toggle options for algorithm
  const [modifiedChartOptions, setModifiedChartOptions] = useState({
    useCovidDataset: false,
    sentimentAnalysis: true,
    window: {
      toggle: true,
      pastSentences: 5,
    },
    neuralNetwork: true,
    useSynonyms: true,
    randomCharts: {
      toggle: true,
      minutes: 5,
      chartWindow: 0,
    },
    threshold: 2,
    filter: {
      toggle: true,
      pastSentences: 5,
      threshold: 2,
    },
    pivotCharts: true,
  });

  // Chart message to send to server
  const [chartMsg, setChartMsg] = useState({
    command: "", //Query
    attributes: [],
    data: "",
    transcript: "",
    uncontrolledTranscript: "",
    datasetTitle: "",
    loggedTranscript: [], // {sentence: string, date: createDate()}
    loggedUncontrolledTranscript: [],
    synonymMatrix: [], //Synonyms used in attributes
    featureMatrix: [], //Unique data values
    explicitChart: [],
    randomCharts: [],
    mainAI: [],
    mainAIOverhearing: [],
    abariCharts: [],
    pivotChart: [],
    deltaTime: 0,
    assistantResponse: "",
    errMsg: "",
    charts: [],
    mainAIOverhearingCount: {
      quantitative: [],
      nominal: [],
      temporal: [],
      map: [],
    },
    total: {
      quantitative: [],
      nominal: [],
      temporal: [],
      map: [],
    },
  });
  //Visual feedback for computer unuted, mute, and thinking
  const [clippyImage, setClippyImage] = useState(listeningImage);

  const [voiceMsg, setVoiceMsg] = useState(null);

  // Handler to show thought bubble for clippy
  const [showTooltip, setShowTooltip] = useState(false);
  useEffect(() => {
    if (showTooltip) {
      setTimeout(() => {
        setShowTooltip(false);
      }, 8000);
    }
  }, [showTooltip]);
  // Handle Request to server
  const createCharts = (command) => {
    if (command) {
      chartMsg.command = command;
    }
    //Pick a random thinking response
    // let thinkingResponse =
    //   thinking[Math.floor(Math.random() * thinking.length)];
    // setClippyImage(thinkingImage);
    // if (command !== "random") {
    //   speakVoice(thinkingResponse.soundFile);
    //   setVoiceMsg(thinkingResponse.msg);
    // }
    setClippyImage(thinkingImage);
    return new Promise((res, rej) => {
      //Actual request to server
      serverRequest(
        chartMsg,
        setChartMsg,
        modifiedChartOptions,
        setVoiceMsg,
        charts,
        setCharts,
        setChartToHighlight
      ).then((response) => {
        console.log(response);

        if (mute) {
          setClippyImage(muteImage);
        } else {
          //Voice syntheiszer
          if (response.assistantResponse) {
            speakVoice(response.assistantResponse.soundFile);
            setVoiceMsg(response.assistantResponse.msg);
            setClippyImage(talkingImage);
            setShowTooltip(true);
            speakVoice(chartSound);
          }
          setTimeout(() => {
            setClippyImage(listeningImage);
          }, 3000);
        }
        res(response.isCommand);
      });
    });
  };

  useEffect(() => {
    if (mute) {
      setClippyImage(muteImage);
    } else {
      setTimeout(() => {
        setClippyImage(listeningImage);
      }, 4000);
    }
  }, [clippyImage]);
  //In chartSelection component, handles choosing the chart to add in
  //Chosen component
  const chooseChart = (chosenChart) => {
    chosenChart.timeChosen.push(createDate());
    chosenChart.visible = true;
    let found = false;
    for (let i = 0; i < charts.length; i++) {
      if (chosenChart == charts[i]) {
        found = true;
      }
    }
    if (!found) {
      setCharts((prev) => [...prev, chosenChart]);
    } else {
      setForceUpdate((prev) => !prev);
    }

    chartMsg.explicitChart = [];
    chartMsg.mainAI = [];
    chartMsg.mainAIOverhearing = [];
  };

  const handleMute = () => {
    setMute((prev) => {
      if (mute) {
        setClippyImage(listeningImage);
      } else {
        setClippyImage(muteImage);
      }
      return !prev;
    });
  };
  const textRef = useRef("");

  const closeChosenCharts = () => {
    for (let i = 0; i < charts.length; i++) {
      charts[i].visible = false;
      charts[i].pivotThis = false;
    }
    setForceUpdate((prev) => !prev);
  };

  const [count, setCount] = useState(0);
  let checker =
    "stop. make us some map. already make a map of the united states. angela. access fl. covid-19. make a chart for a covid risk. kobe bryant pictures. how to draw the numbers. cornerstone church. tell me what are you can help you make me feel like dancing. discuss. can you make a map of counties. all right. party can you filter the histogram by county sites. show battlebots baseball tournament. can we see a chart of population by county. rt filter the map by area type. can you filter the map by area type. hello. i didn't say. are you can you make a map for all counties. i love you. already can you make a heat map for counties versus diabetes. text. rt vicky heat map of covid risk versus region. how do you make a heat heat map chart of region. jennifer todd frederick md. paul messina. can you make a chart of of covid risk versus region. what is the price of mexican food. are they can you make it visualization for mapping midwest rule and high poverty rate. access to the doctors for tonight. vacancy harry potter. are the midwest. you don't sound very high diabetes.. see if it makes sense that i really slow in the midwest. for which reason selfie. are you making seating chart of poverty versus nexus the doctor's filtered by southeast and high poverty rate. can you make a heat map chart of poverty versus access to doctors filtered by southeast and higher poverty rate. hamilton place mall. i think it's supposed to go right.. namaste to jack in the box.. make a heat map chart of poverty versus access to doctors filter by salty's. rt nagar she's not between access to doctors and poverty. already know jesse's not between access to doctors and poverty. make a keypad of access to doctors versus poverty. by region. it is not by region. what's another word filter. can you check this map by region. region. search this map by region. rt select all of the regions in this math. change the color scheme to blue. you want to take another nap instead. i think it's nice to know that it's also very high on the southeast also. access to doctors on cell. are you making map of poverty versus region. how do you make a map of regions versus elderly population. it's a no value. yes.. already making map of southwest plus suburban plus high elderly population plus variable access the doctors. stop speaking up and then she'll be ready. how do you make the map of the southwest and suburban elderly population. thank you. attributes. like this specifically filter. an elderly percentage. bernie tiede. region lies we see the the southeast on the most. histogram. so i got the song. dog beds. can you make a heat map of covid risk. this is what we need. the doctors. no access to doctors. greenville covid-19. health department. stop disturbing i think the correlation is there playing doctors in high-risk on the population as well. the met last time. but at the same time. you make a sheet mask of a chart of covid risk versus region. can you make a heat map of covid risk versus region. read new message.. can you make a heat map of covid risk versus access to doctors. can you make a sheet map chart of colored wrist forces access to doctors. can you make a chart of covid risk versus region. generalized chart chart of covid risk versus region. can you make a chart of covid-19. if it says it can't find it sometimes it means you might already have the chart on the wall. sofia carson. perfect. high poverty rate. trying to do something with cardiovascular disease. i want to put all this in one check. the awesomest. can you make us a chart of covid risk poverty and diabetes. diabetes. can you create a chart of covid vs allergies and diabetes per county. can you make a fart sound of covid-19 and diabetes for county. babies r us. it seems like very high covid-19. it is also funny because you have lack of that in the southeast that seems like all kind of just generalized. i think it was poverty interesting that. can you combine your maps. politico. can you make a map of poverty and covid risk. can you make a map of poverty versus covid risk. can you make a chart of poverty versus cobra dress. perfect. don't you stuff too. can you make this into a heat map. naked. already can you flip the x & y axis fitness chart. i can definitely see this is like kind of like jarvis. i think we just wanted to look into them i don't see what it is. traxxas palmetto beach. as for the middle east or the middle of the midwest. is there something called messages. can you make a map of covid risk by cases. can you make a map of social folder ability by region. no i wanted to. why are you there already can you zoom in on the zoom app. zoom into this map. the best thing we can do is just actually. make a heat map of covid risk vs. type. i don't know.. how do you make a map of covid risk versus area type. arlington you make a heat map of.. coleman furnace filter. can you make a map of covid vs filtered by area tape. party city make a heat not start of covid risk vs area type. truck companies pushing press conference oregon. young just try the other ones dancing. auntie vicky heat make a sheet map of cardiovascular disease. parisian. map of car. we're getting a lot of cardiovascular disease. rt-10 you make a cardiovascular disease map for area code. how do you make a map of the uninsured. cuz i tried in the midwest by population by poverty rate. thank you for the appointment can you make a map of diabetes versus cardiovascular disease versus elderly population. manicures. i want you to come by. denise cazares dealing with three different things. can you make a bar chart of diabetes versus cardiovascular disease in elderly population. for the meantime i think it's heights. that's why. erica herman. make a bar chart of southeast plus vero plus very high poverty rate. open actually the whole thing. or at least before. what she wanted. put the wrong thing. for the meantime it doesn't seem like it would be useful for these questions at the very least. thank you. kayaks for sale. can you show the filters. expect that down for some reason. can you take off high poverty rate filter. can you remove the null value. i don't know, maybe chances specific far. but some correlations of. which regions. we can look at it. cuz i know if we just look at these two maps right here. we already know this stuff is very ipod pretty mixed with the high-risk which is an obvious correlation. every type of mixed together. army time. poverty and covid risk. making sheet map chart of poverty and covid risk. anki heat map of poverty vs. covid risk. make a note between poverty and covid risk. can you make a map between poverty and covid risk. hello. i want to find out. pro fitness in hauppauge. i wish i could put them together. maybe we can do. make a map of poverty filtered by high covid risk. make a map of poverty versus. very high covid risk index. put spinach in action by region. i think we can ready answer. most of it. can you make a map of regions. can you make a map of regions. i know. can you make a map by area size. mickey mouse by area type. can you make a chart of suburban areas. regional acceptance. what is a suburb. make a histogram of region filtered by urban. he really loves giving this afternoon. very high correlation of servants also having high poverty rate. i want to make a map of all the area codes so that. can you make a map of all area type. of the area types. stockton police cars. can you make a map filtered by southwest plus urban plus very high covid risk index. how do you say the same thing just makes it. map region by song. what did i do something wrong. not go away. that's cool. and if it just delete them. nicole. chase's versus killer. i like this song. they all started in november and december. can release the iphone is not caring when it's running. because a correlation with. can you make a line chart of cases versus date colored by area type and region. let's go can you not combine them. give me the line chart of cases versus date colored by area type + region. thank you for talking to a human. can you make a line chart of cases versus fake colored by area type and region. he's like i said go to the doctors. miss a. can you. the kids model picture. let me try this can you remove grill from this map. can you remove burden from the snow. can you remove non-contiguous from this chart. can you remove the rockies from this chart. can you remove the rockies from this chart. what can you do. but i guess it's fine for now. ?. answer clearly if i were talking about like. like then city seems to be the midwest and the southeast. but i want to make the charger so that we can specifically. chris.. can we make a map of regions. jamaica map by region. can you make a map by region. i swear i was working earlier. that's a lot of scrolling.. it gone forever. but that's for everybody that's a lot of. can you make a map by region. i just had a ride. can you make a histogram of region filtered by poverty. can you make a histogram of region versus poverty. can you make a histogram of region and poverty. cheapest early baby. can you make a bar graph of region filtered by very high poverty. can you make a map of regions filtered by very high poverty. cuz anybody nice if we can get it can you make a chart of poverty versus covid virus. okay. but like you're trying to explain it to somebody. which regions of the us should be prioritized it seems like it heavy correlation between the two color coded more in the southwest or the southeast i mean and just the southern countries in general we were trying to mess around with my area size the heat the heat map so we see from this there's a heavy correlation in the southeast and most of the southern country is brisk and something we should prioritize without written resources. in addition to that we noticed that. in addition to that we see with the heat not try to cover the rest versus ice if the doctors";
  let checkerArray = checker.split(".");

  const testRequest = async () => {
    let response = await createCharts(checkerArray[count]);

    console.log(checkerArray[count], response);
    setCount((prev) => prev + 1);
  };

  return (
    <>
      <ChakraProvider>
        <div style={{ display: chartsPage ? null : "None" }}>
          {/* COMMENT THIS WHEN STARTING USER STUDY */}
          {/* <Button onClick={() => speakVoice("This is a message")}>
            Test Voice
          </Button> */}
          <Input
            position="absolute"
            ml="40rem"
            bg="white"
            zIndex={20}
            width={"10rem"}
            ref={textRef}
          ></Input>

          <Button
            position="absolute"
            ml={"50rem"}
            zIndex={20}
            onClick={() => createCharts(textRef.current.value)}
          >
            Test
          </Button>
          <Button onClick={testRequest}>{">"}</Button>

          {/* <Button
            position="absolute"
            ml={"60rem"}
            zIndex={20}
            onClick={() =>
              commandChecker(
                chartMsg,
                modifiedChartOptions,
                setVoiceMsg,
                charts,
                setChartMsg
              )
            }
          >
            Command Checker
          </Button> */}
          {/* COMMENT THIS WHEN STARTING USER STUDY */}

          <ArtyContainer
            clippyImage={clippyImage}
            handleMute={handleMute}
            voiceMsg={voiceMsg}
            mute={mute}
            showTooltip={showTooltip}
          />
          <AttributeContainer
            setChartMsg={setChartMsg}
            modifiedChartOptions={modifiedChartOptions}
            setModifiedChartOptions={setModifiedChartOptions}
            chartMsg={chartMsg}
            setStartStudy={setStartStudy}
            startStudy={startStudy}
          />

          <Charts
            chartMsg={chartMsg}
            setChartMsg={setChartMsg}
            chooseChart={chooseChart}
            charts={charts}
            setCharts={setCharts}
            mute={mute}
            chartToHighlight={chartToHighlight}
            modifiedChartOptions={modifiedChartOptions}
          />
        </div>
        <div style={{ display: !chartsPage ? null : "None" }}>
          <Diagnostics chartMsg={chartMsg} mute={mute} charts={charts} />
        </div>
        <Dictaphone
          createCharts={createCharts}
          setChartMsg={setChartMsg}
          chartMsg={chartMsg}
          voiceMsg={voiceMsg}
          closeChosenCharts={closeChosenCharts}
          mute={mute}
          startStudy={startStudy}
          setClippyImage={setClippyImage}
          setShowTooltip={setShowTooltip}
          setVoiceMsg={setVoiceMsg}
          modifiedChartOptions={modifiedChartOptions}
        />
        <Box position="absolute" top="0" right="0">
          <Button onClick={() => setChartsPage((prev) => !prev)}>
            {chartsPage ? "Diagnostics" : "Charts"}
          </Button>
        </Box>
      </ChakraProvider>
    </>
  );
}

export default App;
