
const clockSource = new EventSource("/get_time");
const clockDisplay = document.getElementById("clock");

const weatherSource = new EventSource("/get_curr_weather_data");
const weatherDisplay = document.getElementById("weather");


const tasksSource = new EventSource("/get_curr_todo");
const taskUl = document.getElementById("todoList");

clockSource.onmessage = function(event){
    clockDisplay.textContent = event.data;
}

weatherSource.onmessage = function(event){
    weatherDisplay.textContent = event.data;
}

tasksSource.onmessage = function(event){
    const tasks = JSON.parse(event.data)
    const tasks_name = []
    for (const task of tasks){
        tasks_name.push(task[1])
    }
    taskUl.innerHTML= "";
    for (const task of tasks_name){
        const newTask = document.createElement("li");
        newTask.textContent = task;
        taskUl.appendChild(newTask);
    }
    
    
}

async function loadCalendar(){
    const response = await fetch("http://localhost:8000/get_calendar");
    const calendar_list = document.getElementById("calendarList")
    const data = await response.json();
    for (const element of data){
        const newEvent= document.createElement("li");
        newEvent.textContent = `${element.title} - ${element.start} - ${element.end}`;
        calendar_list.appendChild(newEvent);
    }
}

loadCalendar();