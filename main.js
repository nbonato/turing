var infoBox = document.getElementById("info-box");

var pressChartWrapper = document.createElement("div");
var pressChart = document.createElement("canvas")
pressChartWrapper.appendChild(pressChart);

var electionChartWrapper = document.createElement("div");
var electionChart = document.createElement("canvas")
electionChartWrapper.appendChild(electionChart);

pressChartWrapper.classList.add("donut-chart-wrapper");
electionChartWrapper.classList.add("donut-chart-wrapper");

// Get the slider element
var slider = document.getElementById("yearSlider");

// Get the value display element
var sliderValue = document.getElementById("sliderValue");

// Display the initial value
sliderValue.innerText = slider.value;

// Define a variable to store the clicked layer
var clickedLayer = null;

// Create the map
var map = L.map('map', {
    zoomControl: false, // Disable zoom control
    minZoom: 5, // Set maximum zoom level
    zoomSnap: 0.5 
}).setView([55.3781, -3.4360], 5);


// Find the first election year that is equal or greater than the target year.
var electionYears = [1847, 1852, 1857, 1859, 1865, 1868, 1874, 1880, 1885, 1886, 1892, 1895, 1900, 1906, 1910, 1918, 1922]

function electionYear(pressYear) {
    let largerYear = null;
    for (const electionYear of electionYears) {
        if (electionYear >= pressYear) {
            largerYear = electionYear;
          return largerYear
        }
    }
}




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
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}


var year = parseInt(slider.value); // Initial value of the year variable
var closestElection = 1847; // First available election
// Removes the attribution watermark
map.attributionControl.setPrefix(''); 
//map.setMaxBounds(map.getBounds());
// Load and add the GeoJSON data layer
//fetch('geodata/UKDefinitionA.json')
fetch('updated_map.json')
    .then(response => response.json())
    .then(data => {        
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
                    // Update the map when the slider value changes
                    let alreadyUpdated = false;
                    slider.addEventListener('mouseup', function () {
                        year = parseInt(this.value);
                        closestElection = electionYear(year);
                        sliderValue.innerText = `You picked ${year}, the closest election was in ${closestElection}`;
                        alreadyUpdated = true;
                        populateInfoBox(feature);
                    });
                    if (alreadyUpdated === false) {
                        populateInfoBox(feature);
                    }
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
                });

                //layer.bindTooltip(feature.properties.NAME, { permanent: true, direction: 'center' }).openTooltip();

            }
        }).addTo(map);

    

    });


function populateInfoBox(feature) {
    console.log(`${feature.properties.NAME} ${year}`);
    // Fetch data from the JSON file
    fetch('new_data.json')
    .then(response => response.json())
    .then(data => {
        // Retrieve the data for the specific key
        var pressChartData = data[feature.properties.NAME.toLowerCase()][year];

        // Create the chart
        chartCreator(pressChart, pressChartData);

    }).catch(error => console.error(error));

    // Fetch data from the JSON file
    fetch('scripts/elections.json')
    .then(response => response.json())
    .then(data => {
        // Retrieve the data for the specific key
        var electionChartData = data[closestElection.toString()][feature.properties.NAME.toLowerCase()];
        // Create the chart
        chartCreator(electionChart, electionChartData);

    }).catch(error => console.error(error));
    infoBox.innerHTML = "";
    var infoBoxContent = document.createElement("div");
    var infoBoxTitle = document.createElement("h2");
    infoBoxTitle.textContent = `${feature.properties.NAME} ${year}`;
    infoBoxContent.className = "chart-container"
    infoBoxContent.appendChild(infoBoxTitle);
    infoBoxContent.appendChild(pressChartWrapper);
    infoBoxContent.appendChild(electionChartWrapper);
    infoBox.appendChild(infoBoxContent);
}