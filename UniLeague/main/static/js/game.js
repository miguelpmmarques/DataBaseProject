if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    console.log("HERE");
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajaxSetup({

        headers: {
            "X-CSRFToken": csrf_token
        }
    });

    var form = document.getElementById("home_form")
    var btn = document.getElementById("addNewGoal");
    btn.addEventListener("click", (e) => {
        if (form.hidden) {
            form.hidden = false;
        } else {
            form.hidden = true;
        }
    })
    var form2 = document.getElementById("rm_form")
    var btn = document.getElementById("removeGoal");
    btn.addEventListener("click", (e) => {
        if (form2.hidden) {
            form2.hidden = false;
        } else {
            form2.hidden = true;
        }

    })
    var ole = $('#timepicker1').timeselector({
        hours12: false,
        min: '00:00',

        max: '01:30',
    })

    $("#home_form").submit(function(e) {
        e.preventDefault();
        var time = $('#timepicker1').val() + ":00";
        var scorer = $("#scorer_input option:selected")[0].value
        var split_time = time.split(":");
        var hours = Number(split_time[0][1]);
        var minutes = Number(split_time[1]);
        var my_time = new Date(year = 0, month = 0, day = 0, hour = hours, minute = minutes);
        var compare_date = new Date(year = 0, month = 0, day = 0, hour = 1, minute = 30);
        console.log("kookok==", my_time.getTime());
        console.log("oioi==", compare_date.getTime());

        if (my_time.getTime() > compare_date.getTime()) {
            alert("Wrong time! Please enter a goal time between 00:00 and 1:30")
        } else {
            $.ajax({
                type: "POST",
                url: "",
                data: JSON.stringify({
                    scorer: scorer,
                    time: time
                }),
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                success: (d) => {
                    window.location.href = "";
                },
                failure: (d) => {
                    console.log(d);
                }
            });
        }



    })
    $("#rm_form").submit(function(e) {
        e.preventDefault();
        var goal = $("#goals_rm option:selected")[0].value
        var result_id = this.name;
        console.log("DELETE===", `/goals/${goal}`);
        $.ajax({
            type: "DELETE",
            url: `/goals/${goal}`,
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: (d) => {},
            failure: (d) => {
                console.log(d);
            }
        });
        console.log("PATCH===", "/results/" + result_id + "/");
        $.ajax({
            type: "PATCH",
            url: "/results/" + result_id + "/",
            data: JSON.stringify({}),

            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: (d) => {
                window.location.href = "";
            },
            failure: (d) => {
                console.log(d);
            }
        });

    })
}