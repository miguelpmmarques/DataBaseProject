if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    $(document).ready(function() {
        $('[data-toggle="tooltip"]').tooltip();
    });
    var success_helper = function(e, type) {
        console.log("DATA:", e);
        console.log("type:", type);
        var ul = document.getElementById(`ul_${type}`)
        console.log("UL::::", ul);
        var elements = ul.getElementsByTagName("li");
        console.log("LIS---->>>", elements);
        var length = elements.length;
        for (i = 0; i < length; i++) {
            console.log(i);
            console.log("ELEM===", elements[0]);
            elements[0].remove();
        }
        if (type == "users") {
            for (elem of e) {
                let extra;
                console.log("OIOI==", elem);
                if (e.isTournamentManager == true) {
                    extra = "(Tournament Manager)";
                } else if (e.isCaptain == true) {
                    extra = "(Captain)";
                } else {
                    extra = "(Player)";
                }
                var li = document.createElement("li");
                li.className = "groupList list-group-item";
                li.appendChild(document.createTextNode(`${elem.first_name} ${elem.last_name} ${extra}`));
                ul.appendChild(li);
            }
        } else {

            for (elem of e) {
                var li = document.createElement("li");
                li.className = "groupList list-group-item";
                li.appendChild(document.createTextNode(`${elem.name}`));
                ul.appendChild(li);
            }
        }
    }
    var failure_helper = function(response_data) {
        console.log(response_data);;
    }
    $("form").submit(function(e) {
        e.preventDefault();
        var type = this.id;
        var data = {
            "name": document.getElementById(`input_${type}`).value
        };
        console.log("DATA====", data);
        $.ajax({
            type: "GET",
            url: `${window.location.origin}/${type}/rest/list/`,
            data: data,
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: (d) => {
                success_helper(d, type);
            },
            failure: failure_helper,
        })
    });
}
