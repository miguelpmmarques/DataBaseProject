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
    var form = document.getElementsByTagName("form")[0]
    var btn = document.getElementById("addNewGoal");
    btn.addEventListener("click", (e) => {
        form.hidden = false;
    })
    var ole = $('#timepicker1').timeselector({
        hours12: false,
        min: '00:00',
        max: '02:00',
    })

    $("form").submit(function(e) {
        e.preventDefault();
        var time = $('#timepicker1').val() + ":00";
        var scorer = $("#scorer_input option:selected")[0].value


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
    })
}