import React, { Component } from "react";

class AudioVisualiser extends Component {
  constructor(props) {
    super(props);
    this.canvas = React.createRef();
  }
  componentDidUpdate() {
    this.draw();
  }
  draw() {
    const { audioData } = this.props;
    const canvas = this.canvas.current;
    const height = canvas.height;
    const width = canvas.width;
    const context = canvas.getContext("2d");
    let x = 0;
    const sliceWidth = (width * 1.0) / audioData.length;
    context.lineWidth = 2;

    var grad = context.createLinearGradient(400, 400, 900, 900);

    grad.addColorStop(0, "blue");
    grad.addColorStop(0.5, "purple");
    grad.addColorStop(1, "teal");

    context.strokeStyle = grad;

    context.clearRect(0, 0, width, height);
    context.beginPath();
    context.moveTo(0, height / 2);
    for (const item of audioData) {
      const y = (item / 255.0) * height;
      context.lineTo(x, y);
      x += sliceWidth;
    }

    context.lineTo(x, height);
    context.stroke();
  }

  render() {
    return <canvas width="2600" height="50" ref={this.canvas} />;
  }
}

export default AudioVisualiser;
