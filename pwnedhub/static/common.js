function show_flash(msg) {
    flash = document.getElementById("flash");
    flash.innerHTML = msg;
    flash.style.visibility = "visible";
    setTimeout(function() { flash.style.visibility = "hidden"; }, 5000);
}

// HTML5 drag and drop functions

function drag_start(event) {
    var style = window.getComputedStyle(event.target, null);
    event.dataTransfer.setData("text/plain", event.target.id + "," + (parseInt(style.getPropertyValue("left"),10) - event.clientX) + "," + (parseInt(style.getPropertyValue("top"),10) - event.clientY));
}

function drag_over(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    return false;
}

function drop(event) {
    var offset = event.dataTransfer.getData("text/plain").split(",");
    var dm = document.getElementById(offset[0]);
    var left = event.clientX + parseInt(offset[1],10);
    var top = event.clientY + parseInt(offset[2],10);
    dm.style.left = left + "px";
    dm.style.top = top + "px";
    event.preventDefault();
    // persist toolbar position
    sessionStorage.setItem("toolbar", left + "," + top);
    return false;
}

window.onload = function() {
    // flash on load if needed
    flash = document.getElementById("flash");
    var msg = flash.innerHTML
    // ;;D-XSS in the error parameter
    var error = document.URL.indexOf("error=");
    if (error !== -1) {
        var msg = decodeURI(document.URL.substring(error+6, document.URL.length)).replace(/\+/g, " ");
    }
    if (msg.length > 0) {
        show_flash(msg);
    }

    // set up drag and drop for the toolbar
    var dm = document.getElementById('draggable');
    if (dm != null) {
        dm.addEventListener('dragstart', drag_start, false);
        document.body.addEventListener('dragover', drag_over, false);
        document.body.addEventListener('drop', drop, false);
        // position toolbar if previously moved
        if (sessionStorage.getItem("toolbar")) {
            var coords = sessionStorage.getItem("toolbar").split(',');
            dm.style.left = parseInt(coords[0],10) + 'px';
            dm.style.top = parseInt(coords[1],10) + 'px';
        }
        dm.style.visibility = "visible";
    }
}
