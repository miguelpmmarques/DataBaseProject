if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    var success_helper = function(e) {
        window.location.href = window.location.origin;
    }
    var failure_helper = function(e) {
        console.log(e);;
    }
    $(document).ready(function() {
        console.log("ready!");
        $('#datepicker').datepicker({
            todayBtn: "linked",
            multidate: true,
            format: 'yyyy-mm-dd',
        });
    });
    $("form").submit(function(e) {
        e.preventDefault();
        var data = new FormData(this);
        var beginTournament = data.get("beginTournament");
        var endTournament = data.get("endTournament");
        var date_begin = new Date(beginTournament);
        var date_end = new Date(endTournament);
        var alert_msg = "";
        var num_hands = data.get("number_of_hands");
        var today = new Date();
        if (date_begin.getTime() > date_end.getTime()) {
            console.log("here");
            alert_msg += " Begining date can't be superior to End Date!"
        }
        if (date_begin.getTime() < today.getTime() || date_end.getTime() < today.getTime()) {
            alert_msg += " Tournament can't take place before today!"
        }
        if (Number(num_hands) < 1) {
            console.log("here2");
            alert_msg += " Your games have to have at least one hand!";
        } else if (Number(num_hands) > 6) {
            console.log("here3");
            alert_msg += " Too many hands to play!";
        }
        if (alert_msg !== "") {
            var msg = document.getElementById("alert");
            msg.innerHTML = alert_msg;
            msg.hidden = false;
            alert_msg = "";
        } else {
            console.log("HERE2");
            $.ajax({
                url: "",
                data: data,
                type: "POST",
                contentType: false,
                processData: false,
                success: success_helper,
                failure: failure_helper,
            })

        }

    });
}