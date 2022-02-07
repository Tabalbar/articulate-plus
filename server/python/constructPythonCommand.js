module.exports = (pythonResponse) => {
  console.log(pythonResponse);
  if (pythonResponse == null) {
    return;
  }
  let createVis = false;
  for (let i = 0; i < pythonResponse.length; i++) {
    if (
      pythonResponse[i].dialogueAct === "modifyvis" ||
      pythonResponse[i].dialogueAct === "createVis"
    ) {
      createVis = true;
      break;
    }
  }

  if (!createVis) {
    return [];
  }
  let plotType = "";
  switch (pythonResponse.visualization_task.plot_type) {
    case "bar chart":
      plotType = "bar";
    case "tree map":
      plotType = "map";
    default:
      plotType = "bar";
  }

  return [];
};
