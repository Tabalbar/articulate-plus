/**
 * Helper to use browser's voice synthesizer
 *
 * @param {string} text What to say
 * @param {bool} mute to handle browser voice synthesizer
 * @returns
 */
function UseVoice(text, mute) {
  var msg = new SpeechSynthesisUtterance();
  var voices = window.speechSynthesis.getVoices();
  msg.voice = voices[49];
  msg.volume = 1; // From 0 to 1
  msg.rate = 1; // From 0.1 to 10
  msg.pitch = 0; // From 0 to 2
  msg.text = text;

  //If muted, don't speak
  if (!mute) {
    window.speechSynthesis.speak(msg);
    msg.onend = (event) => {
      console.log(event.elapsedTime);
    };
  }
  return msg;
}

export default UseVoice;
