document.addEventListener('DOMContentLoaded', function () {
  const socket = io('/updates');

  socket.on('new_event', function (data) {
    const list = document.getElementById('event-updates');
    if (list) {
      const item = document.createElement('li');
      item.textContent = data.title || JSON.stringify(data);
      list.appendChild(item);
    }
  });

  socket.on('new_reminder', function (data) {
    const list = document.getElementById('reminder-updates');
    if (list) {
      const item = document.createElement('li');
      item.textContent = data.message || JSON.stringify(data);
      list.appendChild(item);
    }
  });
});
