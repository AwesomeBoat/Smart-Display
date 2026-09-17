
const clockSource = new EventSource("/get_time")
const clockDisplay = document.getElementById("clock")
clockSource.onmessage = function(event){
    clockDisplay.textContent = event.data
}