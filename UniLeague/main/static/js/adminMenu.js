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
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value

    $.ajaxSetup({
        headers: {
            'X-CSRF-TOKEN': csrf_token
        }
    });

    var success_helper = function(e, type) {
        var ul = document.getElementById(`ul_${type}`)
        var elements = ul.getElementsByTagName("li");
        console.log("LIS---->>>", elements);
        var length = elements.length;
        for (i = 0; i < length; i++) {
            console.log(i);
            elements[0].remove();
        }
        if (type == "users") {
            for (elem of e) {
                let extra;
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
            if (type !== "blacklist") {
                var data = {
                    "name": document.getElementById(`input_${type}`).value
                };
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
            } else {
                const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
                var data = {
                    is_active: false,
                    hierarchy: 0
                };
                $.ajax({
                    type: "PATCH",
                    url: `${window.location.origin}/users/rest/`,
                    data: data,
                    dataType: "json",
                    contentType: "application/json; charset=utf-8",
                    success: (d) => {
                        success_helper(d, type);
                    },
                    failure: failure_helper,
                })
            }
        }
    });

}