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
  var replacement = document.getElementsByClassName('replace');

  console.log(replacement);

  for (var i = 0; i < replacement.length; i++) {

      replacement[i].addEventListener("click", function(e) {
          e.preventDefault();
          askReplacement(this.id);

      });
  }
  var reserve = document.getElementsByClassName('reserve');
  console.log("------------------------------------");
  console.log(reserve);
  for (var i = 0; i < reserve.length; i++) {

    reserve[i].addEventListener("click", function(e) {
      e.preventDefault();
      reserveReplace(this.id);
    });
  }
}

function reserveReplace(pk) {
  console.log(pk);
  var getSelect = document.getElementById('select'+pk);
  var dataHtml = getSelect.options[getSelect.selectedIndex].value;
  dataHtml = dataHtml.split("|")
  console.log(dataHtml);
  var data = {
  "user" : dataHtml[1],
  "replace" : dataHtml[0],
  "team" : dataHtml[2],
  }
  $.ajax({
        url: "/replaceReserve/",
        type: 'PATCH',
        timeout: 3000,
        data : data,
        success: function(d) {
            if (d === "Done") {
              window.location = ''
            }
        },
        data: data
    })
    .fail(function() {
        alert('Error updating this model instance.');
    });

}

function askReplacement(teampk) {
  console.log(teampk);
  var name = document.getElementById('name|'+teampk).value
  var email = document.getElementById('email|'+teampk).value
  var phone = document.getElementById('phone|'+teampk).value
  var until = document.getElementById('until|'+teampk).value

  var data = {
  "name" : name,
  "email" : email,
  "phone" : phone,
  "until" : until
  }
  $.ajax({
        url: "/replaceMember/" +teampk+ "/",
        type: 'PATCH',
        timeout: 3000,
        data : data,
        success: function(d) {
            if (d === "Done") {
              console.log("Top");
            }
        },
        data: data
    })
    .fail(function() {
        alert('Error updating this model instance.');
    });
}
