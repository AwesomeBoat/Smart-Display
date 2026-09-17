
const clockSource = new EventSource("/get_time");
const clockDisplay = document.getElementById("clock");

const weatherSource = new EventSource("/get_curr_weather_data");
const weatherDisplay = document.getElementById("weather");


const tasksSource = new EventSource("/get_todo");
const taskUl = document.getElementById("todoList");

clockSource.onmessage = function(event){
    clockDisplay.textContent = event.data;
}

weatherSource.onmessage = function(event){
    weatherDisplay.textContent = event.data;
}

tasksSource.onmessage = function(event){
    const tasks = JSON.parse(event.data)
    taskUl.innerHTML= "";
    for (const task of tasks){
        const newTask = document.createElement("li");
        newTask.textContent = task;
        taskUl.appendChild(newTask);
    }
    
    
}