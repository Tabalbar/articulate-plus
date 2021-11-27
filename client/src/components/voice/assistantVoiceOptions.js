//duplicate charts
import actuallychartalreadyuphere from "../../sounds/actually chart already.wav";
import alreadyuphere from "../../sounds/already up here.wav";

//thinking
import givemeaseccreate from "../../sounds/give me a sec create.wav";
import givemea from "../../sounds/give me a.wav";
import holdon from "../../sounds/hold on.wav";
import iamcreating from "../../sounds/i am creating.wav";
import ineedtothink from "../../sounds/i need to think.wav";
import letmesee from "../../sounds/let me see.wav";
import letmethink from "../../sounds/let me think.wav";
import workingon from "../../sounds/working on.wav";

//greeting
import hello from "../../sounds/hello.wav";

//one chart
import checkthis from "../../sounds/check this.wav";
import givethis from "../../sounds/give this.wav";
import lookatthis from "../../sounds/look at this.wav";
import heresachart from "../../sounds/heres a chart.wav";
import onechart from "../../sounds/one chart.wav";

//two charts
import hereare2 from "../../sounds/here are 2.wav";
import ihave2 from "../../sounds/i have 2.wav";

//three charts
import hereare3 from "../../sounds/here are 3.wav";
import ihave3 from "../../sounds/i have 3.wav";

//few charts
import checkthese from "../../sounds/check these.wav";
import herearesome from "../../sounds/here are some.wav";
import ihaveafew from "../../sounds/i have a few.wav";
import lookatthese from "../../sounds/look at these.wav";

//no charts
import couldntcreate from "../../sounds/couldnt create.wav";
import sorrycanthelp from "../../sounds/sorry cant help.wav";
import youneedtobe from "../../sounds/youneedtobe.mp3";
import idontknowhow from "../../sounds/i dont know how.wav";

//random charts

export const thinking = [
  { msg: "Let me think about that.", soundFile: letmethink },
  {
    msg: "Give me second to create those charts.",
    soundFile: givemeaseccreate,
  },
  { msg: "I am creating those charts for you now.", soundFile: iamcreating },
  { msg: "I need to think about that", soundFile: ineedtothink },
  { msg: "give me a second", soundFile: givemea },
  { msg: "hold on", soundFile: holdon },
  { msg: "working on it", soundFile: workingon },
  { msg: "let me see", soundFile: letmesee },
];

export const duplicate = [
  {
    msg: "actually, the chart's already up there",
    soundFile: actuallychartalreadyuphere,
  },
  { msg: "The chart's already up there", soundFile: alreadyuphere },
];

export const noCharts = [
  { msg: "I don't know how to make a chart for that", soundFile: idontknowhow },
  { msg: "sorry, cant help you there", soundFile: sorrycanthelp },
  { msg: "I couldn't create any charts for that", soundFile: couldntcreate },
  // { msg: "You need to be more specific", soundFile: youneedtobe },
];

export const oneChart = [
  { msg: "I have one chart for you", soundFile: onechart },
  { msg: "here's a chart", soundFile: heresachart },
  { msg: "Give this a try", soundFile: givethis },
  { msg: "Check this out", soundFile: checkthis },
  { msg: "take a look at this.", soundFile: lookatthis },
];

export const twoCharts = [
  { msg: "I have two charts for you.", soundFile: ihave2 },
  { msg: "here are two charts", soundFile: hereare2 },
  { msg: "take a look at these", soundFile: lookatthese },
  { msg: "check these out", soundFile: checkthese },
];

export const threeCharts = [
  { msg: "I have three charts for you.", soundFile: ihave3 },
  { msg: "here are three charts", soundFile: hereare3 },
  { msg: "take a look at these", soundFile: lookatthese },
  { msg: "check these out", soundFile: checkthese },
];

export const fewCharts = [
  { msg: "here are some charts", soundFile: herearesome },
  { msg: "take a look at these", soundFile: lookatthese },
  { msg: "check these out", soundFile: checkthese },
  { msg: "i have a few charts for you", soundFile: ihaveafew },
];
