if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
  var btns = document.getElementsByClassName("btn");
  console.log(btns)

  for (var i = 0; i < btns.length; i++) {
    btns[i].addEventListener('click', myFunction);
  }

  function myFunction(e){
    $.ajax({url: "",
          type: 'PATCH', timeout: 3000, data: { 'team': this.id }//, processData:false, contentType = 'application/json'
      })
      .fail(function(){
          alert('Error viewing this team.');
      });

  }
}
