function show_flash(msg) {
    flash = document.getElementById("flash");
    flash.innerHTML = msg;
    flash.style.visibility = "visible";
    setTimeout(function() { flash.style.visibility = "hidden"; }, 5000);
}

window.onload = function() {
    // flash on load if needed
    flash = document.getElementById("flash");
    if (flash.innerHTML.length > 0) {
        show_flash(flash.innerHTML);
    }
}
