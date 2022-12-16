/**
 * Copyright (c) 2021-2023 Roderick Tabalba University of Hawaii at Manoa
 * Laboratory for Advanced Visualizations and Applications (LAVA)
 *
 *
 */
var speech_voices;
if ("speechSynthesis" in window) {
  speech_voices = window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = function () {
    speech_voices = window.speechSynthesis.getVoices();
  };
}
export default function speakVoice(soundFile) {
  var audio = new Audio(soundFile);
  audio.play();
}
