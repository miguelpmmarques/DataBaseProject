if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
  $("form").submit(function(e) {
      var val = $("input[type=submit][clicked=true]").val();
      console.log(val);
      e.preventDefault();
  })
  const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrf_token }
  });
    var btns = document.getElementsByClassName("btn");
    console.log(btns)

    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', myFunction);
    }
    function myFunction(e){
      $.ajax({url: "",
            type: 'PATCH', data: { 'position': this.id }//, processData:false, contentType = 'application/json'
        }).done(function(d){
          console.log(d);
          if (d=="success"){
            window.location.href = window.location.origin;
          }
        })
        .fail(function(){
            alert('Position already filled!');
        });

    }


}
