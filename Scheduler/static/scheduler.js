
const STATE = {
    // Window being shown
    current_state: "state_a",
    // User data
    name : "",
    email : "",
    objective : "",
    duration: "0",
    date: "0",
    time: "",
    // Site data
    dayMap : { 0:"S", 1:"M", 2:"T", 3:"W", 4:"TH", 5:"F", 6:"SA" },
    timeslots: [],
    parsedDays : {}
}

function on_start() {
    // Load first gui
    load_layout("state_a");
    // Get available times from server
    $.ajax({
        type:"GET",
        dataType:"json",
        url:"/scheduler/get_available_times",
        success: function (response) {
            for (let i in response) {
                let [start, end] = response[i];
                STATE.timeslots.push([new Date(start), new Date(end)]);
            };
            load_days();
        },
        error: function () {
            alert("ajax error occured");
        } 
    });
    
}

function load_layout(ele) {
    // set initial state
    $("#hidden").append($("#"+STATE.current_state));
    $("#shown").append($("#"+ele))
    STATE.current_state = ele;
}

function submit_state_a() {  
    STATE.name = $("#nameInput").val();  
    STATE.email = $("#emailInput").val();
    STATE.objective = $("#objectiveInput").val();
    load_layout("state_b");
}

function submit_state_b() {
    // Display the user data for confirmation
    $("#nameConfirm").text("Name: " + STATE.name);
    $("#emailConfirm").text("Email: " + STATE.email);
    $("#dateConfirm").text("Date: " + STATE.date);
    $("#timeConfirm").text("Time: " + $(STATE.time).text());
    $("#objectiveConfirm").text("Objectives: " + STATE.objective);
    load_layout("state_c");
}

function submit_final() {
    $.ajax({
        type:"GET",
        dataType:"json",
        url:"/scheduler/post_meeting",
        data : {
            "name":STATE.name,
            "email":STATE.email,
            "start": $(STATE.time).attr("id"),
            "duration":STATE.duration,
            "objective":STATE.objective
        },
        success: function (response) {
            $("#final-notification").text(response["msg"]);
        },
        error: function () {
            alert("ajax error occured");
        } 
    });

    $(STATE.time).attr("id");
    }

function load_days() {
    // This function should be called whenever a duration is selected.
    // It will display all the available days when there are times
    // open with the required duration.
    let days = []
    // function to find if a date exists within days 
    // I'm using this to make sure there are no duplicate days.
    // collect all available days.
    for (let i in STATE.timeslots) {
        // Get datetime beginning of timeslot
        let date = STATE.timeslots[i][0];
        // Convert datetime into string rep of date
        let isoString = (1+date.getMonth()) + "/" + date.getDate() + " (" + STATE.dayMap[date.getDay()] + ")";
        // Determining if the next timeslot occurs on a day already in days
        if (!days.includes(isoString)) {
            days.push(isoString);
            let cell = $("<div>", {
                id:(date.getMonth()+1) + "-" + date.getDate(),
                class:"cell day", 
                text:isoString 
            });        
            cell.on("click",function () {select_day(this);});
            $("#daylist").append(cell)
        }
    }
}


function load_throbber() {
    $("#times").innerHTML = "";
    $("#times").append($("#throbber"));
}

function hide_throbber() {
    $("#hidden").append($("#throbber"));

}

function load_times() { 
    $("#timelist").empty();
    for (let i in STATE.timeslots) {
        let start = new Date(STATE.timeslots[i][0]);
        let end = new Date(STATE.timeslots[i][1]);
        while ((end-start)/1000/60 >= STATE.duration) {
            // Calculating start times of openings for the chosen day
            let time_str = start.getHours() + ":" + start.getMinutes()
            if (start.getMinutes() == 0) { time_str += "0"; };
            // Creating div to display times
            let time = $("<div>", {  
                id : start.toISOString(),
                class : "cell time",
                text : time_str
            });
            $("#timelist").append(time);
            // Adding onclick function
            time.on("click", function() { select_time(this);} );
            // Advancing start to the next opening
            start.setMinutes(start.getMinutes() + 15);
        }
    }

}

function select_duration(selected) {
    // selected can be div with id, or obj with id.
    if (STATE.duration != "0") {
        $("#"+STATE.duration).removeClass("chosen");
    };
    STATE.duration = selected.id;
    $(selected).addClass("chosen");
    if (STATE.date != "0") {
        load_times();
    };
}

function select_day(selected) {
    if (STATE.date != "0") {
        $("#"+STATE.date).removeClass("chosen");
    };
    STATE.date = selected.id;
    $(selected).addClass("chosen");
    if (STATE.duration != 0) {
        load_times();
    };
}

function select_time(selected) {
    $(STATE.time).removeClass("chosen");
    STATE.time = selected;
    $(selected).addClass("chosen");
}
