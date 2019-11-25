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
