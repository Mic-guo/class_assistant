// function addClass() {
//     var classInput = document.getElementById('classInput');
//     var course = classInput.value.trim();

//     if (course !== '') {
//         var listItem = document.createElement('li');
//         listItem.textContent = skill;

//         var classList = document.getElementById('classList');
//         classList.appendChild(listItem);

//         classInput.value = '';
//     }
// }

document.querySelector("#addClassBtn").addEventListener("click", function() {
    var classInput = document.getElementById('classInput');
    var course = classInput.value.trim();

    if (course !== '') {
        var listItem = document.createElement('li');
        listItem.textContent = skill;

        var classList = document.getElementById('classList');
        classList.appendChild(listItem);

        classInput.value = '';
    }
});