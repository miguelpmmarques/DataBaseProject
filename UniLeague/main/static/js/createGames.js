if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    var createGames = document.getElementsByName("createGames")[0]
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajaxSetup({

        headers: {
            "X-CSRFToken": csrf_token
        }
    });
    createGames.addEventListener("click", function(e) {
        $.ajax({
                url: "/games/generate/" + createGames.id + "/",
                type: 'POST',
                timeout: 3000,
                data: {
                    "team_creation": true
                }, //, processData:false, contentType = 'application/json'
                success: function(d) {
                    console.log("DATA==", d);
                    window.location.href="";
                }, //, processData:false, contentType = 'application/json'
            })
            .fail(function() {
                alert('Error updating this model instance.');
            });
    })
}
