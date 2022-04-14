// js

let inputFile = document.getElementById("select-file");
let Filename = document.getElementById("file-name");
inputFile.addEventListener("change", function(event){
    let uploadFile = event.target.files[0].name;
    Filename.textContent = uploadFile;
})