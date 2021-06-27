module.exports = () => {
    let date = new Date()
    const [month, day, year] = [date.getMonth(), date.getDate(), date.getFullYear()];
    let [hour, minutes, seconds] = [date.getHours(), date.getMinutes(), date.getSeconds()];
    let amOrPm = "AM"
    if(hour >= 12) {
        hour = hour - 12
        amOrPm = "PM"
    }
    if(hour == 0) {
        hour = 12
    }
    if(minutes < 10) {
        minutes = "0" + minutes
    }
    if(seconds < 10) {
        seconds = "0" + seconds
    }
    date = "Date: " + month + "/" + day + "/" + year + " Time: " + hour + ":" + minutes + ":" + seconds + " " + amOrPm
    return date
}