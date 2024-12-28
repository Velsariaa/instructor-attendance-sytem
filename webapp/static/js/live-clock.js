function updateTime() {
  const now = new Date();
  const dateElement = document.getElementById('date');
  const formattedDate = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  dateElement.textContent = formattedDate;
}

function updateClock() {
  const now = new Date();
  const clockElement = document.getElementById('clock');
  let hours = now.getHours();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12; // Convert hours to 12-hour format
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  const timeString = `${hours}:${minutes}:${seconds} ${ampm}`;
  clockElement.textContent = timeString;
}

// Update clock and date every second
setInterval(() => {
  updateTime();
  updateClock();
}, 1000);

// Initial call to update clock and date
updateTime();
updateClock();