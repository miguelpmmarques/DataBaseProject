if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
  $("form").submit(function(e) {
      e.preventDefault();
  })
  const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
  $.ajaxSetup({

    headers: { "X-CSRFToken": csrf_token }
  });
    var success_helper = function(e) {
        window.location.href = window.location.origin;
    }
    var failure_helper = function(e) {
        console.log(e);
    }
    var btns = document.getElementsByClassName("btn");
    console.log(btns)

    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', myFunction);
    }
    function myFunction(e){
      $.ajax({url: "",
            type: 'PATCH', timeout: 3000, data: { 'position': this.id }//, processData:false, contentType = 'application/json'
        })
        .fail(function(){
            alert('Error updating this model instance.');
        });

    }


}
