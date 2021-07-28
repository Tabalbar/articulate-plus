function UseVoice(text, mute) {
  var msg = new SpeechSynthesisUtterance();
  var voices = window.speechSynthesis.getVoices();
  msg.voice = voices[1];
  msg.volume = 1; // From 0 to 1
  msg.rate = 1; // From 0.1 to 10
  msg.pitch = 0; // From 0 to 2
  msg.text = text;

  if (!mute) {
    window.speechSynthesis.speak(msg);
    msg.onend = (event) => {
      console.log(event.elapsedTime);
    };
  }
  return msg;
}

export default UseVoice;
