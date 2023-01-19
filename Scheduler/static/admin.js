const time_offset = new Date().getTimezoneOffset()
const sunday = new Date();
let appointment_dict = {};
const status_dict = {"u":"Unconfirmed", "c":"confirmed","r":"rescheduled","a":"archived"}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (const element of cookies) {
            const cookie = element.trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function conv_utc(date) {
    // converts to utc
    return new Date(date.getTime() - (date.getTimezoneOffset()*60*1000))   
}

function conv_local(date) {
    // converts to local time
    return new Date(date.getTime() + (offset*60*1000)) 
}

function on_start() {
    sunday.setDate(sunday.getDate()-sunday.getDay());
    // alert("This prototype is not checking credentials. Use of RSA certificates needs to be added.")
    load_week();
}


function create_appointment_row(index, date,name, email) {
    let new_row = $("<div>", {id:index, "class": "row underscored"});
    new_row.append($("<div class='cell'><h6>"+date+"</h3></div>", {"class":"col-2"}));
    new_row.append($("<div class='cell'><h6>"+name+"</h6></div>", {"class":"col-4"}));
    new_row.append($("<div class='cell'><h6>"+email+"</h6></div>", {"class":"col-4"}));
    $("#appmnt-list").append(new_row);
    new_row.click(function() { select_appointment(this); })
}

function select_appointment(ele) {
    
    //Deselect selected appointment
    $(".selected").removeClass("selected");
    ele.classList.add("selected");
    $("#previous-meetings").empty()
    //ajax call to get appointment data

    $.ajax({
        type:"POST",
        dataType:"json",
        url:"/scheduler/get_meeting_details",
        headers: {'X-CSRFToken': csrftoken},
        data: { id:ele.id},
        success: function (response) {
            $("#meetings-container").append($("<div>", { class:"row", text: "Selected meeting:"}));
            add_meeting_detail(response);
            $("#meetings-container").append($("<div>", { class:"row", text:"Other meetings with Contact:"}));
            for (let i in response["previous_meetings"]) {
                add_meeting_detail(response["previous_meetings"][i]); 
            }
        },
        error: function () {
            alert("ajax error occured");
        }
    });
 }

 function add_meeting_detail(data)  {
    
    let row = $("<div>", {class:"row border"});
    let col1 = $("<div>", {class:"col-6"});
    col1.append($("<div>", {class:"row"}).text("Name: " +data["name"]));
    col1.append($("<div>", {class:"row"}).text("Email: " + data["email"]));
    col1.append($("<div>", {class:"row"}).text("Date: " + new Date(data["start"]).toLocaleDateString()));
    col1.append($("<div>", {class:"row"}).text("Time: " + new Date(data["start"]).toLocaleTimeString()));
    col1.append($("<div>", {class:"row"}).text("Duration: " + data["duration"]));
    col1.append($("<div>", {class:"row"}).text("Status: " + data["status"]));

    if (data["status"] == "u") {
        col1.append($("<button>", {type:"Button", text:"Confirm", click: function() { 
            update_status(data["id"],"confirm") }})); 
    };

    if (["u","c"].includes(data["status"])) {
        col1.append($("<button>", {text:"Reschedule", click: function() { 
            update_status(data["id"],"reschedule") }}));
    }
     
    if (data["status"] != "a") {
        col1.append($("<button>", {text:"Archive", click: function() { 
            update_status(data["id"], "archive") }}));
        col1.append($("<button>", {text:"Delete", click: function() { 
            update_status(data["id"], "delete") }}));
    }
    row.append(col1);

    let col2 =  $("<div>", {class:"col-6"});
    col2.append($("<div>", {class:"row"}).text("objective: " + data["objective"]));
    col2.append($("<div>", {class:"row"}).text("Note: "))
    col2.append($("<textarea>", {
        class:"row", rows:"2", cols:"25", val:data["note"]
    }));
    col2.append($("<button>", {type:"button", text:"Submit note.", click: function() {
            update_note(data["id"], row.find("textarea").val());
        }}));
    row.append(col2);


    $("#meetings-container").append(row);
 }


function show_report(name) {
    $.ajax({
        type:"POST",
        headers: {'X-CSRFToken': csrftoken},
        dataType:"json",
        url:"/scheduler/get_report/",
        data: { name:name},
        success: function (response) {
            let new_win = window.open("", "Report" );
            new_win.document.write("name,email,start,end,objective,duration,note<br>");
            for (let meeting of response) {
                new_win.document.write(
                    meeting["name"] + ", " + meeting["email"] + ", " + meeting["start"] + 
                    meeting["end"] + ", " + meeting["objective"] + ", " + meeting["duration"] +
                    ", " + meeting["note"] + "<br>")
            }
        },
        error: function () {
            alert("ajax error occured");
        }
    });    
}

function update_status(id, action) {
    $.ajax({
        type:"POST",
        headers: {'X-CSRFToken': csrftoken},
        dataType:"json",
        url:"/scheduler/"+action+"_meeting",
        data: { id:id},
        success: function (response) {
            alert(response["result"]);
        },
        error: function () {
            alert("ajax error occured");
        }
    });
}

function update_note(id, note) {
    alert("update note for meeting [" + id +"] [" + note +"]");
    $.ajax({
        type:"POST",
        dataType:"json",
        headers: {'X-CSRFToken': csrftoken},
        url:"/scheduler/update_note",
        data: { id:id, note:note},
        success: function (response) {
            alert(response);
        },
        error: function () {
            alert("ajax error occured");
        }
    });
    alert("Update finished");

}

function prev_week() {
    sunday.setDate(sunday.getDate() - 7);
    load_week();
}

function next_week() {
    sunday.setDate(sunday.getDate() + 7);
    load_week();
}

function load_week() {
    $("#weekly-schedule").empty();
    $("#week-title").empty();
    $("#appmnt-list").empty();
    $("#week-title").append("<h6>"+sunday.toDateString()+"</h6>");

    //Add all timeslots for each day of the week
    let end = new Date();
    end.setFullYear(sunday.getFullYear());
    end.setMonth(sunday.getMonth());
    end.setDate(sunday.getDate()+7);

    //Make api call to get all current timeslots     
    $.ajax({
        type:"GET",
        dataType:"json",
        url:"/scheduler/get_timeslots",
        data: {
            //Requesting only timeslots for the currently selected week
            start:sunday.toISOString(),
            end:end.toISOString()
        },
        success: function (response) {
            //Loop through all timeslots returned by api call
            for (let i in response) {
                //Each timeslot has start and end times
                start = new Date(response[i].start);
                end = new Date(response[i].end);
                //Displaying each timeslot with 'delete' button
                let new_slot = $("<div>", {class:"timeslot"}).appendTo("#weekly-schedule");
                let button = $("<button/>", { text:"Delete", click: function() {
                    delete_timeslot(response[i].id);
                }
                });
                new_slot.append(
                    $("<h6>" + start.toLocaleString() + " to " + end.toLocaleString()+"</h6>"),
                    button
                );
            }
        },
        error: function () {
            alert("ajax error occured");
        }
    });

    // Make api call to get all current meetings
    $.ajax({
        type:"POST",
        dataType:"json",
        url:"/scheduler/get_meetings",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            //Requesting only timeslots for the currently selected week
            start:sunday.toISOString(),
            end:end.toISOString()
        },
        success: function (response) {
            for (let i in response) {
                appointment_dict = response[i];
                let date = new Date(appointment_dict["start"]);
                let new_row = $("<div>", {id: appointment_dict["id"], "class": "row underscored"});
                new_row.append($("<div><h6>"+date.toLocaleDateString()+"--"+date.toLocaleTimeString()+"</h6></div><br>"));
                new_row.append($("<div><h6>::"+appointment_dict["duration"] + " mins</h6></div><br>", {"class":"cell"}));
                new_row.append($("<div class='cell'><h6><B>"+appointment_dict["name"]+"</B></h6></div>", {"class":"col-4"}));
                new_row.append($("<div class='cell'><h6>"+appointment_dict["email"]+"</h6></div>", {"class":"col-4"}));
                $("#appmnt-list").append(new_row);
                new_row.click(function() { select_appointment(this); })
            }
        },
        error: function () {
            alert("ajax error occured");
        }
    });

}

function add_timeslot() {

    $("#loading-timeslot-submit").css({opacity:'1'});
    let start = new Date($("#ts-start").val());
    let end = new Date($("#ts-end").val());
    $.ajax({
        type: "POST",
        dataType: "json",
        url:"/scheduler/add_timeslot",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            "start":start.toISOString(),
            "end":end.toISOString()
        },

        success: function (response) {
            $("#loading-timeslot-submit").css({opacity:'0'});
            alert(response["result"]);
            load_week();
        },
        error: function () {
            alert("ajax error occured");
        }
    })

}

function delete_timeslot(id) {
    $.ajax({
        type:"POST",
        dataType:"json",
        url:"/scheduler/delete_timeslot",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            "id":id
        },
        success: function (response) {
            alert(response["result"]);
            if (response["result"]) {load_week(); }
            else { alert("No objects were removed.")}
        },
        error: function () {
            alert("ajax error occured");
        }
    })
}