function show_flash(msg) {
    flash = document.getElementById("flash");
    flash.innerHTML = msg;
    flash.style.visibility = "visible";
    setTimeout(function() { flash.style.visibility = "hidden"; }, 5000);
}

function save_text(filename, content) {
    if (confirm("Save as an artifact?") == true) {
        $.ajax({
            url: "{{ url_for('artifacts_save', method='text') }}",
            type: "POST",
            data: {
                filename: filename,
                content: content,
            },
            success: function(data){
                show_flash(data.message);
            }
        });
    }
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
}
