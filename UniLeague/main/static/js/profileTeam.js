if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}


function main() {
    var changeCaptain = document.getElementById("changeCaptain");
    changeCaptain.addEventListener("click", changeCaptainFun);
}

function changeCaptainFun(e, button) {
    var spinner = document.getElementById('spinner');
    spinner.hidden = false;
    var data = [];
    var urls = [];
    data.push({
        "isCaptain": false
    })
    data.push({
        ""
    })
    $.ajax({
            url: "",
            type: 'PATCH',
            timeout: 3000,
            data: {
                'isCaptain': false
            } //, processData:false, contentType = 'application/json'
        })
        .fail(function() {
            alert('Error updating this model instance.');
        });
}