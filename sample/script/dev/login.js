$(document).ready( () => {
    var person = prompt("Please enter your name", "Harry Potter");
    if (person != null) {
        $('#dynamic-content').append(`<p>${person} is here</p>`);
    }
});