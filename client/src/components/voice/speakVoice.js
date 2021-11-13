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
