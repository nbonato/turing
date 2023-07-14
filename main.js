var pressChartWrapper = document.createElement("div");
var pressChart = document.createElement("canvas")
pressChartWrapper.appendChild(pressChart);

var electionChartWrapper = document.createElement("div");
var electionChart = document.createElement("canvas")
electionChartWrapper.appendChild(electionChart);

// Define a variable to store the clicked layer
var clickedLayer = null;

// Create the map
var map = L.map('map', {
    zoomControl: false, // Disable zoom control
    minZoom: 5, // Set maximum zoom level
    zoomSnap: 0.5 
}).setView([55.3781, -3.4360], 5);



// Function to create the chart

function chartCreator(canvas, data) {
    // Get the existing chart instance
    let existingChart = Chart.getChart(canvas);

    // Destroy the existing chart if it exists
    if (existingChart) {
        existingChart.destroy();
    }

    // Extract labels and values from the data
    var labels = Object.keys(data);
    var values = Object.values(data);

    new Chart(canvas.getContext('2d'), {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
            data: values
            }]
        },
        options: {
            cutout: 50, // Make it a donut chart
            responsive: true,
            maintainAspectRatio: true
        }
    });
}



// Removes the attribution watermark
map.attributionControl.setPrefix(''); 
//map.setMaxBounds(map.getBounds());
// Load and add the GeoJSON data layer
//fetch('geodata/UKDefinitionA.json')
fetch('updated_map.json')
    .then(response => response.json())
    .then(data => {
        // Update the map when the slider value changes
        document.getElementById('yearSlider').addEventListener('mouseup', function () {
            year = parseInt(this.value);
            geojsonLayer.eachLayer(function (layer) {
                if (layer === clickedLayer && layer.isPopupOpen()) {
                    layer.getPopup().setContent(pressChartWrapper);
                }
            });
        });
        var year = 1846; // Initial value of the year variable

        var geojsonLayer = L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: "#ff7800",
                    color: "#000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                layer.on('click', function () {
                    //console.log(`${feature.properties.NAME} ${year}`);

                    // Change the style of the clicked feature
                    layer.setStyle({
                        fillColor: 'red'
                    });
                    // Store the clicked layer and its popup
                    clickedLayer = layer;
                    // Reset the style for all other features
                    geojsonLayer.eachLayer(function (otherLayer) {
                        if (otherLayer !== layer) {
                            geojsonLayer.resetStyle(otherLayer);
                        }
                    });
                    // Fetch data from the JSON file
                    fetch('new_data.json')
                    .then(response => response.json())
                    .then(data => {
                        // Retrieve the data for the specific key
                        var pressChartData = data[feature.properties.NAME.toLowerCase()][year];

                        // Create the chart
                        chartCreator(pressChart, pressChartData);

                        // Create the chart
                        chartCreator(electionChart, pressChartData);

                    }).catch(error => console.error(error));
                    var popupContent = document.createElement("div");
                    var popupTitle = document.createElement("h2");
                    popupTitle.textContent = `${feature.properties.NAME} ${year}`;
                    popupContent.className = "chart-container"
                    popupContent.appendChild(popupTitle);
                    popupContent.appendChild(pressChartWrapper);
                    popupContent.appendChild(electionChartWrapper);
                    layer.bindPopup(popupContent, {className: "popup"}).openPopup();
                });

                //layer.bindTooltip(feature.properties.NAME, { permanent: true, direction: 'center' }).openTooltip();

            }
        }).addTo(map);

        // Function to get the updated popup content based on the feature and year
        function getPopupContent(feature) {
            return `${feature.properties.NAME}, ${year}`;
        }
    });
