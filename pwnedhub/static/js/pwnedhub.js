// add the format method to the String object to add string formatting behavior
String.prototype.format = function() {
    a = this;
    for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
    }
    return a
}

function showFlash(msg) {
    var div = document.createElement("div");
    div.className = "center-content rounded shaded";
    div.innerHTML = msg;
    var id = "flash-" + Date.now();
    div.id = id
    var flash = document.getElementById("flash");
    flash.appendChild(div);
    setTimeout(function() {
        flash.removeChild(document.getElementById(id));
    }, 5000);
}

function cleanRedirect(event, url) {
    event.preventDefault();
    event.stopPropagation();
    window.location = url;
}

function confirmRedirect(event, url) {
    if (confirm("Are you sure?")) {
        cleanRedirect(event, url);
    }
}

function cleanSubmit(event, form) {
    event.preventDefault();
    event.stopPropagation();
    form.submit();
}

function confirmSubmit(event, form) {
    if (confirm("Are you sure?")) {
        cleanSubmit(event, form);
    }
}

function toggleShow(btn) {
    var el = document.getElementById("password");
    var icon = btn ? btn.querySelector("i") : null;
    if (el.type == "password") {
        el.type = "text";
        if (icon) {
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        }
    } else {
        el.type = "password";
        if (icon) {
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }
    }
}

window.addEventListener("load", function() {
    // flash on load if needed
    var queryString = window.location.search;
    var urlParams = new URLSearchParams(queryString);
    var error = urlParams.get('error')
    if (error !== null) {
        showFlash(error);
    }

    // event handler for tab navigation
    var tabs = document.querySelectorAll(".tabs > input[type='radio']")
    var panes = document.querySelectorAll(".tab-content > div")
    tabs.forEach(function(tab) {
        tab.addEventListener("click", function(evt) {
            panes.forEach(function(pane) {
                pane.classList.remove("active");
            });
            document.querySelector(evt.target.value).classList.add("active");
        });
    });
});
