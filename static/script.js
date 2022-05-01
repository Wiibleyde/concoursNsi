// js

let inputFile = document.getElementById("select-file");
let Filename = document.getElementById("file-name-display");
inputFile.addEventListener("change", function(event){
    let uploadFile = event.target.files[0].name;
    Filename.textContent = uploadFile;
})

function load(){
    document.getElementById("textload").style.display = "block";
    document.getElementById("loadbutton").style.display = "none";
}