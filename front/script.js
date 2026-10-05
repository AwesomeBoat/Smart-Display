
const clockSource = new EventSource("/clock/get_time");
const clockDisplay = document.getElementById("clock");

const weatherSource = new EventSource("/weather/get_curr_weather_data");
const weatherDisplay = document.getElementById("weather");


const tasksSource = new EventSource("/todo/get_curr_todo");
const taskUl = document.getElementById("todoList");
const taskCount = document.getElementById("taskCount");

clockSource.onmessage = function(event){
    clockDisplay.textContent = event.data;
}

weatherSource.onmessage = function(event){
    weatherDisplay.textContent = event.data;
}

tasksSource.onmessage = function(event){
    const tasks = JSON.parse(event.data)
    const doneCount = tasks.filter(task => task.done).length
    taskCount.textContent = `${doneCount} / ${tasks.length} validées`;
    taskUl.innerHTML= "";
    for (const task of tasks){
        const newTask = document.createElement("li");
        newTask.textContent = task.done ? `✓ ${task.name}` : task.name;
        taskUl.appendChild(newTask);
    }
}

const habitsSource = new EventSource("/habits/get_curr_habits");
const habitUl = document.getElementById("habitList");
let lastHabitsData = "";

habitsSource.onmessage = function(event){
    // the server sends the same data every second: only redraw when it changed
    if (event.data === lastHabitsData){
        return;
    }
    lastHabitsData = event.data;

    const habits = JSON.parse(event.data);
    habitUl.innerHTML = "";
    for (const habit of habits){
        const newHabit = document.createElement("li");
        newHabit.textContent = `${habit.name} - streak : ${habit.streak}`;
        habitUl.appendChild(newHabit);
    }
}

// the server pushes the active profile calendar: follows profile switches
const calendarSource = new EventSource("/calendar/get_curr_calendar");
const calendarList = document.getElementById("calendarList");
let lastCalendarData = "";

calendarSource.onmessage = function(event){
    // only redraw when the data changed
    if (event.data === lastCalendarData){
        return;
    }
    lastCalendarData = event.data;

    const events = JSON.parse(event.data);
    const now = new Date();
    calendarList.innerHTML = "";
    for (const element of events){
        // hide past events
        if (new Date(element.end) >= now){
            const newEvent = document.createElement("li");
            newEvent.textContent = `${element.title} - ${element.start} - ${element.end}`;
            calendarList.appendChild(newEvent);
        }
    }
}