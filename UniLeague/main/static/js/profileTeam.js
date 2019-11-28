if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {

    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajaxSetup({

        headers: {
            "X-CSRFToken": csrf_token
        }
    });
    console.log("ATAO?");
    get_games_next_week();
    var leave = document.getElementById("leave");
    leave.addEventListener("click", function(e) {
        var r = confirm("Are you certain you want to leave this team?!");
        if (r == true) {
            leaveTeam(leave);
        }
    });
    var options = document.getElementById("exampleFormControlSelect1");
    var captain = options.value;
    var changeCaptain = document.getElementById("changeCaptain");
    changeCaptain.addEventListener("click", function(e) {
        var r = confirm("Are you certain you want to change the captain?!");
        if (r == true) {
            changeCaptainFun(e, captain, options);
        }
    });

    var changePosition = document.getElementsByClassName('btn btn-light btn-outline-secondary changePos');
    for (var i = 0; i < changePosition.length; i++) {

        changePosition[i].addEventListener("click", function(e) {
            e.preventDefault();
            console.log("Clicou");
            changePositionSubs(this.id.split("|"));

        });
    }

    var saveInfo = document.getElementsByClassName('btn btn-default saveInfo');
    for (var i = 0; i < saveInfo.length; i++) {

        saveInfo[i].addEventListener("click", function(e) {
            e.preventDefault();

            saveBudgetAbsences(this.id);

        });
    }
    var convocatoria = document.getElementsByClassName('btn btn-light btn-outline-secondary convocatoria')[0];
    console.log(convocatoria);
    convocatoria.addEventListener("click", function(e) {

        e.preventDefault();
        sendNotifications(this.id);
    });
}

function sendNotifications(teampk) {
    console.log("BATEU " + teampk);
    $.ajax({
            url: "/notifyteam/" + teampk + "/",
            type: 'PATCH',
            timeout: 3000,
            success: function(d) {
                if (d === "Done") {
                    console.log("Top");
                }
            }, //, processData:false, contentType = 'application/json'
        })
        .fail(function() {
            alert('Error updating this model instance.');
        });
}

function saveBudgetAbsences(mypk) {
    var budget = document.getElementById("budget|" + mypk).value
    var absences = document.getElementById("absences|" + mypk).value
    console.log(budget);
    console.log(absences);

    mypk = mypk.split("|")
    data = {
        "budget": budget,
        "absences": absences
    }
    $.ajax({
            url: "/updateTeamUserInfo/" + mypk[0] + "/" + mypk[1] + "/",
            type: 'PATCH',
            timeout: 3000,

            data: data,
            success: function(d) {
                if (d === "Done") {
                    console.log("Done");
                }
            },
            data: data //, processData:false, contentType = 'application/json'
        })
        .fail(function() {
            alert('Error updating this model instance.');
        });
}

function changePositionSubs(mypk) {
    data = {
        "playerpk": mypk[0],
        "teampk": mypk[1]
    }

    $.ajax({
            url: "/positionchange/" + mypk[0] + "/" + mypk[1] + "/",
            type: 'PATCH',
            timeout: 3000,

            data: data, //, processData:false, contentType = 'application/json'
            success: function(d) {
                if (d === "Done") {
                    $('#showPositions').fadeOut('fast').load(' #showPositions > *').fadeIn("fast");
                    $('#ul_users').load(' #ul_users > *', function(responseText, textStatus, XMLHttpRequest) {
                        var changePosition = document.getElementsByClassName('btn btn-light btn-outline-secondary changePos');
                        for (var i = 0; i < changePosition.length; i++) {

                            changePosition[i].addEventListener("click", function(e) {
                                e.preventDefault();
                                changePositionSubs(this.id.split("|"));

                            });
                        }
                        var saveInfo = document.getElementsByClassName('btn btn-default saveInfo');
                        for (var i = 0; i < saveInfo.length; i++) {

                            saveInfo[i].addEventListener("click", function(e) {
                                e.preventDefault();
                                saveBudgetAbsences(this.id);

                            });
                        }

                    });
                }
            },
            data: data
        })
        .fail(function() {
            alert('Error updating this model instance.');
        });
}

function changeCaptainFun(e, old_captain, options) {
    var spinner = document.getElementById('spinner');
    var my_team_id = document.getElementById('myTeam').getAttribute("name");;
    var selected = options.value;
    var data = [];
    var urls = [];
    console.log("HERERER");
    console.log(selected);
    console.log(old_captain);
    if (selected !== old_captain) {
        console.log(selected);
        spinner.hidden = false;
        data.push({
            isCaptain: false
        })
        data.push({
            captain: selected
        });
        data.push({
            isCaptain: true
        })
        urls.push(`${window.location.origin}/teamusers/rest/${old_captain}/`);
        urls.push(`${window.location.origin}/teams/rest/${my_team_id}/`);
        urls.push(`${window.location.origin}/teamusers/rest/${selected}/`)
        for (elem in urls) {
            console.log(data[elem]);
            console.log(urls[elem]);
            console.log(elem);

            $.ajax({
                    url: urls[elem],
                    type: 'PATCH',
                    timeout: 3000,

                    data: data[elem], //, processData:false, contentType = 'application/json'
                    success: function(d) {
                        if (elem == 2) {
                            spinner.hidden = true;
                            window.location.href = "";
                        }
                    },

                    data: data[elem] //, processData:false, contentType = 'application/json'
                })
                .fail(function() {
                    alert('Error updating this model instance.');
                });

        }

    }
}

function leaveTeam(leave) {
    console.log(`/teamusers/rest/${leave.name}/`);
    $.ajax({
            url: `/teamusers/rest/${leave.name}/`,
            type: 'DELETE',
            timeout: 3000,
            success: function(d) {
                console.log("HERER BITCH==", d);
                $('#ul_users').load(' #ul_users > *', function(responseText, textStatus, XMLHttpRequest) {
                    var changePosition = document.getElementsByClassName('btn btn-light btn-outline-secondary changePos');
                    for (var i = 0; i < changePosition.length; i++) {

                        changePosition[i].addEventListener("click", function(e) {
                            e.preventDefault();
                            changePositionSubs(this.id.split("|"));

                        });
                    }
                    var saveInfo = document.getElementsByClassName('btn btn-default saveInfo');
                    for (var i = 0; i < saveInfo.length; i++) {

                        saveInfo[i].addEventListener("click", function(e) {
                            e.preventDefault();
                            saveBudgetAbsences(this.id);

                        });
                    }

                });
            },
        })
        .fail(function() {
            alert('Error updating this model instance.');
        });

}

function get_games_next_week() {
    console.log("HERE");
    var ul = document.getElementById("games_next_week");
    $.ajax({
        type: "GET",
        url: `/games/week/${ul.getAttribute("name")}/`,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: (d) => {
            success_populate_list(d, ul);
        },
        failure: (d) => {
            console.log("OLE===", d);
        }
    });
}

function success_populate_list(data, ul) {
    console.log("data=== ", data);
    for (elem of data) {
        let li = document.createElement("li");
        li.id = elem.id;
        let a = document.createElement("a");
        var date = new Date(elem.start_time);
        a.innerHTML = `${elem.title} at ${date}`
        a.setAttribute("href", `/games/${elem.game.id}/`)
        li.appendChild(a);
        ul.appendChild(li)
    }
}