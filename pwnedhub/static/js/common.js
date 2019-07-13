// add the format method to the String object to add string formatting behavior
String.prototype.format = function() {
    a = this;
    for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
    }
    return a
}

function show_flash(msg) {
    var flash = document.getElementById("flash");
    flash.innerHTML = msg;
    flash.style.visibility = "visible";
    setTimeout(function() { flash.style.visibility = "hidden"; }, 5000);
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

function toggle_show() {
    var el = document.getElementById("password");
    if (el.type =="password") {
        el.type = "text";
    } else {
        el.type = "password";
    }
}

window.addEventListener("load", function() {
    // flash on load if needed
    var flash = document.getElementById("flash");
    var msg = flash.innerHTML
    var error = document.URL.indexOf("error=");
    if (error !== -1) {
        var msg = decodeURI(document.URL.substring(error+6, document.URL.length)).replace(/\+/g, " ");
    }
    if (msg.length > 0) {
        show_flash(msg);
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
