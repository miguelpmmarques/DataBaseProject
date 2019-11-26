if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function createChildren(text, ul, has_icon = true) {
    var li = document.createElement("li");
    if (has_icon) {
        var button = document.createElement("button");
        button.setAttribute("name", "button");
        button.setAttribute("id", "blacklist");
        button.setAttribute("data-toggle", "tooltip");
        button.setAttribute("title", "Click to Add player to BlackList");
        button.className = "float-right";
        li.appendChild(button);
        var icon = document.createElement("i");
        icon.className = "fas fa-ban";
        button.append(icon);
    }
    li.className = "groupList list-group-item";
    li.appendChild(document.createTextNode(text));
    ul.appendChild(li);
}

function main() {
    var lis = document.getElementsByName("users_li");
    for (elem of lis) {
        elem.addEventListener("click", function(e) {

            if (e.target.getAttribute("name") === "users_li") {
                window.location.href = `/users/profile/${e.currentTarget.id}/`

            } else if (e.target.disabled === undefined) {

                $(function() {

                    var data = JSON.stringify({
                        is_active: false,
                        hierarchy: 0
                    })
                    $.ajax({
                        type: "PATCH",
                        url: `${window.location.origin}/users/rest/${e.target.getAttribute("name")}/`,
                        data: data,
                        dataType: "json",
                        contentType: "application/json; charset=utf-8",
                        success: (d) => {
                            for (elem of document.getElementsByName(e.target.getAttribute("name"))) {
                                elem.disabled = true;
                            }
                            alert("User Deactivated");
                        },
                        failure: failure_helper,
                    });
                });
            }
        });
    }
    var success_helper = function(e, type) {
        var ul = document.getElementById(`ul_${type}`)
        var elements = ul.getElementsByTagName("li");
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
                createChildren(`${elem.first_name} ${elem.last_name} ${extra}`, ul);
            }
        } else {

            for (elem of e) {
                createChildren(`${elem.name}`, ul, false);
            }
        }
    }
    var failure_helper = function(response_data) {
        console.log(response_data);;
    }
    $("form").submit(function(e) {
        e.preventDefault();
        var type = this.id;
        if (type !== "blacklist" &&
            type !== "blacklist_i") {
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
            });
        }

    })
}
