Chart.register(ChartDataLabels);

var infoBox = document.getElementById("info-box");
var pressChartWrapper = document.createElement("div");
var pressChart = document.createElement("canvas")
pressChartWrapper.appendChild(pressChart);

var electionChartWrapper = document.createElement("div");
var electionChart = document.createElement("canvas")
electionChartWrapper.appendChild(electionChart);

pressChartWrapper.classList.add("donut-chart-wrapper");
electionChartWrapper.classList.add("donut-chart-wrapper");

// Define geojsonLayer outside so it's accessible by the select element
let geojsonLayer;


// Get the value display element
var yearSelectValue = document.getElementById("year-select-value");

const yearSelect = document.getElementById('year-select');
// Display the initial value
yearSelectValue.innerText = yearSelect.value;

// Define a variable to store the clicked layer
var clickedLayer = null;

// Create the map
var map = L.map('map', {
    zoomControl: false, // Disable zoom control
    minZoom: 5, // Set maximum zoom level
    zoomSnap: 0.5 
}).setView([55.3781, -3.4360], 5);

// Block users from panning away from the map
map.setMaxBounds(map.getBounds());

document.getElementById("reset-button").onclick = function() {
    map.setView([55.3781, -3.4360], 5);
};
// Find the first election year that is equal or greater than the target year.
var electionYears = [1847, 1852, 1857, 1859, 1865, 1868, 1874, 1880, 1885, 1886, 1892, 1895, 1900, 1906, 1910, 1918, 1922]
var year = parseInt(yearSelect.value); // Initial value of the year variable
var closestElection = electionYear(year); // First available election

var county = "";


// Function to calculate the next closest election year
function electionYear(pressYear) {
    let largerYear = null;
    for (const electionYear of electionYears) {
        if (electionYear >= pressYear) {
            largerYear = electionYear;
        return largerYear
        }
    }
}

// Function to find the intersection of two lists
function findIntersection(list1, list2) {
    const intersection = [...new Set(list1)].filter(item => list2.includes(item));
    return intersection;
}

// Function to update the map and info box
function updateView(county, year) {



    // Use the localStorage datasets

    // Retrieve the data for the specific key
    var pressChartData = pressDirectories[year][county.toLowerCase()];
    if (typeof(pressChartData) === "undefined") {
        infoBox.innerHTML = "No press data"
        return
    };
    // Create the chart
    chartCreator(pressChart, pressChartData);

    // Retrieve the data for the specific key
    var electionChartData = elections[closestElection.toString()][county.toLowerCase()];

    if (typeof(electionChartData) === "undefined") {
        infoBox.innerHTML = "No press data"
        return
    };
    // Create the chart
    chartCreator(electionChart, electionChartData, "bar");

    infoBox.innerHTML = "";
    var infoBoxContent = document.createElement("div");
    var infoBoxTitle = document.createElement("h2");
    infoBoxTitle.textContent = `${county} ${year}`;
    infoBoxContent.className = "chart-container"
    infoBoxContent.appendChild(infoBoxTitle);
    infoBoxContent.appendChild(pressChartWrapper);
    infoBoxContent.appendChild(electionChartWrapper);
    infoBox.appendChild(infoBoxContent);
}

// Function to create the chart

function chartCreator(canvas, data, chart_type = "doughnut") {
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
        type: chart_type,
        data: {
            label: "Chart",
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
                    display : false
                }
            }
        }
    });
}


// Function to fetch and store JSON data in local storage
function fetchAndStoreJSON(url, key) {
	return fetch(url)
		.then((response) => response.json())
		.then((data) => {
			localStorage.setItem(key, JSON.stringify(data));
			return data;
		});
}

// Function to check if data is present in local storage
function checkLocalStorage(key) {
	const data = localStorage.getItem(key);
	return data ? JSON.parse(data) : null;
}

// Function to initialize the web app after data is ready
function initializeWebApp(elections, pressDirectories) {
    

    Object.keys(pressDirectories).forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.textContent = option;
        optionElement.value = option; // Set the value if needed
        yearSelect.appendChild(optionElement);
    });

    // Update the map when the select value changes
    yearSelect.addEventListener('change', function () {
        year = parseInt(this.value);
        closestElection = electionYear(year);
        yearSelectValue.innerText = `You picked ${year}, the closest election was in ${closestElection}`;

        // Create a list of available counties for the year
        let relevantPressCounties = Object.keys(pressDirectories[year]);

        let availableCounties = findIntersection(Object.keys(elections[closestElection]), relevantPressCounties);

        // Loop through the GeoJSON features and update fillColor based on selectedYear
        geojsonLayer.eachLayer(function (layer) {
            if (availableCounties.includes(layer.feature.properties.NAME.toLowerCase())) {
                layer.setStyle({
                    fillColor: "green"
                });
            }
            //console.log(layer.feature.properties.NAME);
            
        });

        updateView(county, year);
    });
    // Removes the attribution watermark
    map.attributionControl.setPrefix(''); 
    // Load and add the GeoJSON data layer
    fetch('updated_map.json')
        .then(response => response.json())
        .then(data => {        
            geojsonLayer = L.geoJSON(data, {
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
                        county = feature.properties.NAME;
                        updateView(county, year);
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
                }
            }).addTo(map);

        

        });
}

// Initialise datasets variables
var elections;
var pressDirectories;

// Main function to handle the process
function initializeApp() {
    const electionsData = checkLocalStorage("elections");
	const pressDirectoriesData = checkLocalStorage("pressDirectories");

	if (electionsData && pressDirectoriesData) {
		// Data exists in local storage, use it directly
		elections = electionsData;
		pressDirectories = pressDirectoriesData;

		// Call the web app initialization function
		initializeWebApp(elections, pressDirectories);
	} else {
		// Data does not exist in local storage, fetch and store them
		Promise.all([
			fetchAndStoreJSON("scripts/elections.json", "elections"),
			fetchAndStoreJSON("new_data.json", "pressDirectories"),
		])
			.then(([elections, pressDirectories]) => {
				// Call the web app initialization function
				initializeWebApp(elections, pressDirectories);
			})
			.catch((error) => {
				console.error("Error fetching and storing JSON data:", error);
			});
	}

    electionYears = Object.keys(electionsData);

}

// Call the main function to initialize the app
initializeApp();


