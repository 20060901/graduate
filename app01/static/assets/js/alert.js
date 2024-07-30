function sealert(e) {
    $('body').append("<div class='alert alert-success' id='msg'><strong>" + e + "</strong></div>")
    clearmsg()
}

function dealert(e) {
    $('body').append("<div class='alert alert-danger' id='msg'><strong>" + e + "</strong></div>")
    clearmsg()
}

function clearmsg() {
    var t = setTimeout(function () {
        $("#msg").remove()
    }, 2000)
}