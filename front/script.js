
const clockSource = new EventSource("/get_time")
const clockDisplay = document.getElementById("clock")

const weatherSource = new EventSource("/get_curr_weather_data")
const weatherDisplay = document.getElementById("weather")


clockSource.onmessage = function(event){
    clockDisplay.textContent = event.data
}

weatherSource.onmessage = function(event){
    weatherDisplay.textContent = event.data
}