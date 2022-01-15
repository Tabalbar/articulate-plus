/**
 * Create current dates for logging:
 * transcript
 * When Charts were chosen
 * When charts were deleted
 * @returns Current Date (string)
 */
export default function createDate() {
  let date = new Date();
  const [month, day, year] = [
    date.getMonth(),
    date.getDate(),
    date.getFullYear(),
  ];
  let [hour, minutes, seconds] = [
    date.getHours(),
    date.getMinutes(),
    date.getSeconds(),
  ];
  let amOrPm = "AM";
  if (hour >= 12) {
    hour = hour - 12;
    amOrPm = "PM";
  }
  if (hour == 0) {
    hour = 12;
  }
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  date = hour + ":" + minutes + ":" + seconds + " " + amOrPm;
  return date;
}
