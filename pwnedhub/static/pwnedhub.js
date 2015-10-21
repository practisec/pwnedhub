function execute(path) {
    id = document.getElementById("tool").options[document.getElementById("tool").selectedIndex].value;
    name = document.getElementById("tool").options[document.getElementById("tool").selectedIndex].text;
    args = document.getElementById("args").value;
    // execute the command
    minAjax({
        url: path,
        type: "POST",
        data: {
            tool: id,
            args: args,
        },
        success: function(data){
            // update the textarea with the command output
            output = document.getElementById("output");
            result = JSON.parse(data);
            output.innerHTML = result.output;
        }
    });
}
