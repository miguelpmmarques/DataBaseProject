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
    var options = document.getElementById("exampleFormControlSelect1");
    var captain = options.value;
    var changeCaptain = document.getElementById("changeCaptain");
    changeCaptain.addEventListener("click", function(e) {
        var r = confirm("Are you certain you want to change the captain?!");
        if (r == true) {
            changeCaptainFun(e, captain, options);
        }
    });
    var changePosition = document.getElementsByClassName('changePos');
    for (var i=0; i<changePosition.length;i++) {
      changePosition[i].addEventListener("click",function(e) {
          changePositionSubs(this.id)

      });
    }
}
function changePositionSubs(mypk) {
  data = {"replacePk" : this.id}
  $.ajax({
          url: urls[elem],
          type: 'PATCH',
          timeout: 3000,

          data: data, //, processData:false, contentType = 'application/json'
          success: function(d) {
          },
          data: data[elem]//, processData:false, contentType = 'application/json'
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
        urls.push(`${window.location.origin}/users/rest/${old_captain}/`);
        urls.push(`${window.location.origin}/teams/rest/${my_team_id}/`);
        urls.push(`${window.location.origin}/users/rest/${selected}/`)
        console.log("data===", data);
        console.log("urls===", urls);
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
                        console.log("INDEX====", elem);
                        if (elem == 2) {
                            console.log("HEREREREER");
                            spinner.hidden = true;
                            window.location.href = window.location.origin;
                        }
                    },

                    data: data[elem]//, processData:false, contentType = 'application/json'
                })
                .fail(function() {
                    alert('Error updating this model instance.');
                });

        }

    }
}
