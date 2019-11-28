if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
      main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
  console.log("bom dia");
  const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
  $.ajaxSetup({

      headers: {
          "X-CSRFToken": csrf_token
      }
  });
  var reserve = document.getElementsByClassName('apllyReserve')[0];
  console.log(reserve);
  console.log("bom tarde");

  reserve.addEventListener("click",function(e) {
      console.log(e)

      createReserveFunction(this.id);

  });
    jQuery(document).ready(function($) {
        $(".clickable-row").click(function() {
            window.location = $(this).data("href");
        });
    });
}

function createReserveFunction(tournamentpk){

  $.ajax({
          url: "/addReserve/" + tournamentpk + "/",
          type: 'PATCH',
          timeout: 3000,
          success: function(d) {
              if (d === "Done") {
                  console.log("Done");
              }
          },
      })
      .fail(function() {
          alert('Error updating this model instance.');
      });
}
