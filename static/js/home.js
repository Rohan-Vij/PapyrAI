
// Adapted from https://stackoverflow.com/a/35588057/
const getNextDay = (day, time) => {
  const now = new Date();

  const nextDay = new Date();
  nextDay.setDate(now.getDate() + (day - 1 - now.getDay() + 7) % 7 + 1);
  nextDay.setHours(...time);

  return nextDay;
}

const getTimeRemaining = (date) => {
  const time = (date - new Date()) / 1000;
  const floor = Math.floor;

  const seconds = floor(time % 60);
  const minutes = floor((time / 60) % 60);
  const hours = floor((time / 60 / 60) % 24);
  const days = floor(time / 60 / 60 / 24);

  return { days, hours, minutes, seconds };
}

const padNum = (num) => {
  return num.toString().padStart(2, "0");
}

window.onload = () => {
  const timerElement = document.getElementById("timer");
  const nextFriday10AM = getNextDay(5, [10, 0, 0, 0]);
  
  setInterval(() => {
    const { days, hours, minutes, seconds } = getTimeRemaining(nextFriday10AM);
    timerElement.textContent = `${padNum(days)} : ${padNum(hours)} : ${padNum(minutes)} : ${padNum(seconds)}`;
  }, 1000);
}

