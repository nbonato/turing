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

const radioButtons = document.querySelectorAll('input[name="display-dataset"]');
var displayDataset = document.querySelector('input[name="display-dataset"]:checked').value;



// Define a colour scheme and display the relevant legend
const colourScheme = {
    "liberal": 'red',
    "multiple majority": "forestgreen",
    "independent": "gray",
    "neutral": "DarkSlateGray",
    "conservative": '#034EA2',
    "undefined": "gold",
    "unionist" : "MidnightBlue",
    "constitutional": "Olive",
    "nationalist": "Tomato",
    "liberal; unionist": "BlueViolet",
    "liberal; conservative": "purple",
    "independent; liberal": "pink",
    "no-politics": "gold",
    "whig": "orange",
    "other" : "fuchsia"
};

const legendDiv = document.getElementById('legendDiv');

for (const label in colourScheme) {
  const color = colourScheme[label];
  const legendItem = document.createElement('div');
  legendItem.className = 'colour-scheme-legend-item';
  legendItem.innerHTML = `
    <div class="colour-scheme-square" style="background-color: ${color};"></div>
    ${label}
  `;
  legendDiv.appendChild(legendItem);
} 





// Define geojsonLayer outside so it's accessible by the select element
let geojsonLayer;


// Get the value display element
var yearSelectValue = document.getElementById("year-select-value");



// Define a variable to store the clicked layer
var clickedLayer = null;

// Create the map
var map = L.map('map', {
    zoomControl: false, // Disable zoom control
    minZoom: 4.5, // Set maximum zoom level
    zoomSnap: 0.25 
}).setView([55.3781, -3.4360], 4.5);

// Block users from panning away from the map
map.setMaxBounds(map.getBounds());

document.getElementById("reset-button").onclick = function() {
    map.setView([55.3781, -3.4360], 4.5);
    infoBox.innerHTML = "Click on any available county to see the data. If a county is grayed out, it means that there are no press information on it for that year, so try moving around the slider above.";

};
// Find the first election year that is equal or greater than the target year.
var electionYears = [1847, 1852, 1857, 1859, 1865, 1868, 1874, 1880, 1885, 1886, 1892, 1895, 1900, 1906, 1910, 1918, 1922]

var pressYears = [1846]
var year = pressYears; // Initial value of the year variable
var closestElection = electionYear(year); // First available election

var county = "";



// Test range
const range = document.querySelector(".range");
const bubble = document.querySelector(".bubble");



function titleCase(string){
    return string[0].toUpperCase() + string.slice(1).toLowerCase();
}

// Create a function to snap the slider to the nearest year in the list
function snapToYear(value) {
  const closestYear = pressYears.reduce((closestYear, year) => {
    const distance = Math.abs(year - value);
    return distance < Math.abs(closestYear - value) ? year : closestYear;
  }, pressYears[0]);
  return closestYear;
}

function setBubble(range, bubble) {
  const val = range.value;
  const min = range.min ? range.min : 0;
  const max = range.max ? range.max : 100;
  const newVal = Number(((val - min) * 100) / (max - min));
  bubble.innerHTML = val;

  // Numbers based on size of the native UI indicator
  bubble.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`;
}



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

// Function to update the map

function updateMap(geojsonLayer) {
    geojsonLayer.resetStyle();
    let updateDataset;
    let updateYear;
    if (displayDataset === "Press") {
        updateDataset = pressDirectories;
        updateYear = year;
    } else {
        updateDataset = elections;
        updateYear = closestElection;
    };


    let availableCounties = Object.keys(updateDataset[updateYear]);


    // Loop through the GeoJSON features and update fillColor based on selectedYear
    geojsonLayer.eachLayer(function (layer) {
        let countyName = layer.feature.properties.NAME.toLowerCase();
        if (availableCounties.includes(countyName)) {
            let majorityColour = colourScheme[updateDataset[updateYear][countyName]["majority"]]
            layer.setStyle({
                fillColor: majorityColour,
                color: majorityColour
            });

        } else {
            layer.setStyle({
                fillColor: "gainsboro",
                opacity: 1,
                color: "lightgray"
            });
        }
        //console.log(layer.feature.properties.press_county);
        
    });

}

// Function to update the info box
function updateView(county, year) {

    // Retrieve the data for the specific key
    var pressChartData = pressDirectories[year][county.toLowerCase()];
    if (county != "") {
        if (typeof(pressChartData) === "undefined") {
            infoBox.innerHTML =`${county} no press data`;
            console.log(county, year, closestElection); 
            return
        };
    } else {
        infoBox.innerHTML = "Click on any available county to see the data. If a county is grayed out, it means that there are no press information on it for that year, so try moving around the slider above.";
        return
    };
    
    // Create the chart
    chartCreator(pressChart, pressChartData["press_data"]);

    // Retrieve the data for the specific key
    var electionChartData = elections[closestElection.toString()][county.toLowerCase()];

    if (typeof(electionChartData) === "undefined") {
        infoBox.innerHTML ="no election data";
        console.log(county, year, closestElection);
        return
    };
    // Create the chart
    chartCreator(electionChart, electionChartData, "bar");

    infoBox.innerHTML = "";
    var infoBoxContent = document.createElement("div");
    var infoBoxTitle = document.createElement("h3");
    infoBoxTitle.textContent = `${titleCase(county)} press in ${year}`;
    infoBoxContent.className = "chart-container"
    infoBoxContent.appendChild(infoBoxTitle);
    infoBoxContent.appendChild(pressChartWrapper);
    infoBoxContent.appendChild(electionChartWrapper);
    infoBox.appendChild(infoBoxContent);
}

// Function to create the chart

function chartCreator(canvas, data, chart_type = "doughnut") {


    if (chart_type == "bar") {
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
                labels: [county],
                datasets: [{
                    label: "Liberal Party (Original)",
                    data: [1],
                 },{
                    label: "Conservative",
                    data: [1],
                 }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: true,
                title: { display: true, text: `Electoral results in ${closestElection}`},
                plugins: {
                    legend: {
                        position: "top"
                    }
                }
            }
        });

    } else {
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
                    data: values,
                    backgroundColor: labels.map(label => colourScheme[label]),

                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    datalabels : {
                        color: "white"
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

   
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
    
    pressYears = Object.keys(pressDirectories)
    // Set the minimum and maximum values of the slider
    range.min = pressYears[0];
    range.max = pressYears[pressYears.length - 1];


    setBubble(range, bubble);
    // Store the old value to fire the script in the event listener
    // only when the range has actually changed
    let oldRange = range.value;
    // Update the map when the select value changes
    range.addEventListener("input", () => {
        range.value = snapToYear(range.value);
        if (range.value != oldRange) {
            year = parseInt(snapToYear(range.value));
            setBubble(range, bubble);
            closestElection = electionYear(year);
            yearSelectValue.innerText = `You picked ${year}, the closest election was in ${closestElection}`;

            updateMap(geojsonLayer);
            updateView(county, year);

            oldRange = range.value;
        }

    });
    
    // Removes the attribution watermark
    map.attributionControl.setPrefix(''); 
    // Load and add the GeoJSON data layer
    fetch('updated_map.json')
        .then(response => response.json())
        .then(data => {        
            geojsonLayer = L.geoJSON(data, {
                style: {
                    weight: 1,
                    fillOpacity: 0.9
                    
                },
                onEachFeature: function (feature, layer) {
                    layer.on('click', function () {
                        county = feature.properties.NAME.toLowerCase();
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
            updateMap(geojsonLayer);
        

        });

    radioButtons.forEach(radioButton => {
        radioButton.addEventListener('change', (event) => {
            displayDataset = event.target.value;
            updateMap(geojsonLayer);
        });
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
			fetchAndStoreJSON("press_data.json", "pressDirectories"),
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


