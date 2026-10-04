
const clockSource = new EventSource("/clock/get_time");
const clockDisplay = document.getElementById("clock");

const weatherSource = new EventSource("/weather/get_curr_weather_data");
const weatherDisplay = document.getElementById("weather");


const tasksSource = new EventSource("/todo/get_curr_todo");
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
        tasks_name.push(task.name)
    }
    taskUl.innerHTML= "";
    for (const task of tasks_name){
        const newTask = document.createElement("li");
        newTask.textContent = task;
        taskUl.appendChild(newTask);
    }
    
    
}

const habitsSource = new EventSource("/habits/get_curr_habits");
const habitUl = document.getElementById("habitList");
let lastHabitsData = "";

habitsSource.onmessage = function(event){
    // the server sends the same data every second: only redraw when it changed,
    // otherwise the buttons are rebuilt under the mouse and a click can be lost
    if (event.data === lastHabitsData){
        return;
    }
    lastHabitsData = event.data;

    const habits = JSON.parse(event.data);
    habitUl.innerHTML = "";
    for (const habit of habits){
        const newHabit = document.createElement("li");
        newHabit.textContent = `${habit.name} - streak : ${habit.streak} `;

        const doneButton = document.createElement("button");
        doneButton.textContent = "Fait aujourd'hui";
        doneButton.onclick = function(){
            fetch(`/habits/add_log/${habit.id}`, {method: "POST"});
        };

        newHabit.appendChild(doneButton);
        habitUl.appendChild(newHabit);
    }
}

async function loadCalendar(){
    const response = await fetch("http://localhost:8000/calendar/get_calendar");
    const calendar_list = document.getElementById("calendarList")
    const data = await response.json();
    const now = new Date();
    for (const element of data){
        const elementEnd = new Date(element.end);
        if (elementEnd >= now){
        const newEvent= document.createElement("li");
        newEvent.textContent = `${element.title} - ${element.start} - ${element.end}`;
        calendar_list.appendChild(newEvent);
        }
    }
}

loadCalendar();