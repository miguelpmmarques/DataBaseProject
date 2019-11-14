if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    var success_helper = function(e) {
        window.location.href = window.location.origin;
    }
    var failure_helper = function(e) {
        console.log(e);;
    }
    $("form").submit(function(e) {
        e.preventDefault();
        var data = new FormData(this);

        $.ajax({
            url: "",
            data: data,
            type: "POST",
            contentType: false,
            processData: false,
            success: success_helper,
            failure: failure_helper,
        })
    });
}