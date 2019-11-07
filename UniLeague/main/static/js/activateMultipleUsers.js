if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    const activate_user = document.getElementById("activate_users");
    activate_users.addEventListener("click", function(e) {
        activateMultipleUsers(e);
    })
}

function activateMultipleUsers(e) {
    let users_to_activate = document.getElementsByTagName("input");
    console.log("users===", users_to_activate);
    let aux_url_array = window.location.href.split("/");
    this.loading = true;
    let reqData = [];
    for (elem of users_to_activate) {
        if (elem.id && elem.checked) {
            let obj = {};
            obj[String(elem.id)] = {
                is_active: true
            };
            reqData.push(obj)
        }
    }
    console.log("OLOLE:::>", reqData);
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    try {
        fetch(`http://127.0.0.1:8000/users/rest/list/`, {
            method: "PATCH",
            credentials: "include",
            headers: {
                "X-CSRFToken": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(reqData),
        }).then(response => {
            response.json().then(data => {
                console.log("Data:", data);
                this.loading = false;
            });
        });
    } catch (e) {
        console.log(e, "erro");
        setTimeout(() => {
            patch_user_data();
        }, this.loadInterval);
    }
}