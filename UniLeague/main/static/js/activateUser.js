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
    })
}

function activateThisUser(e) {
    let aux_url_array = window.location.href.split("/");
    let usr_id = Number(aux_url_array[aux_url_array.length - 2])
    console.log("aux_array==", aux_url_array);
    this.loading = true;
    let reqData;
    reqData = {
        is_active: true,
    }
    const csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    try {
        fetch(`${window.location.origin}/users/rest/${usr_id}`, {
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