var map = L.map('map').setView([-1, 36], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);




function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on('draw:created', function(e) {
    var layer = e.layer;
    drawnItems.addLayer(layer);

    // Get coordinates
    var coordinates = layer.toGeoJSON().geometry.coordinates;
    console.log('coordinates are', coordinates)
    const url = '/index-api/';

    // Send coordinates to Django backend using fetch
    fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin', // Do not send CSRF token to another domain.
            body: JSON.stringify({ coordinates: coordinates })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);

            }

            console.log(response)
            return response.json();
        })
        .then(data => {
            // Handle the response data
            console.log('Response:', data);

            const mapDiv = document.getElementById('map');
            mapDiv.innerHTML = data.map
        })
        .catch(error => {
            console.error('Error sending data:', error);
            return error.text(); // This line will get the response text
        })
        .then(responseText => {
            console.log('Server Response:', responseText);
        });
});