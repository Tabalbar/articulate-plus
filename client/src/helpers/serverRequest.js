import UseVoice from '../components/voice/UseVoice'
export async function serverRequest(chartMsg, setChartMsg) {


    const response = await fetch('/createCharts', {
        method: 'POST',
        body: JSON.stringify(
            {
                chartMsg
            }),
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    });
    const body = await response.text();
    // console.log(JSON.parse(body.chartMsg))
    const responseChartMsg = JSON.parse(body)
    let tmpChartMsg = responseChartMsg.chartMsg
    console.log(tmpChartMsg)
    setChartMsg(tmpChartMsg)
    let utterance = UseVoice(tmpChartMsg.assistantResponse)
    return utterance
}