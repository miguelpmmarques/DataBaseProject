if (document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)) {
    main();
} else {
    document.addEventListener("DOMContentLoaded", main);
}

function main() {
    const activate_user = document.getElementById("activate_user");
    activate_user.addEventListener("click", function(e) {
        activateThisUser(e);
        erase_not_button(e);
    })
}

function activateThisUser(e) {
    let aux_url_array = window.location.href.split("/");
    let usr_id = Number(aux_url_array[aux_url_array.length - 2])
    this.loading = true;
    let reqData;
    reqData = {
        is_active: true,
    }
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    try {
        fetch(`${window.location.origin}/users/rest/${activate_user.name}/`, {
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
                this.loading = false;
                window.location.href = ""
            });
        });
    } catch (e) {
        setTimeout(() => {
            patch_user_data();
        }, this.loadInterval);
    }
}

function erase_not_button(e) {
    var not = document.getElementById("not");
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    var reqData = {
        html: ""
    }
    try {
        fetch(`${window.location.origin}/notifications/rest/${not.name}/`, {
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
        setTimeout(() => {
            erase_not_button();
        }, this.loadInterval);
    }

}
