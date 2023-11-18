function addClass() {
    var classInput = document.getElementById('classInput');
    var course = classInput.value.trim();

    if (course !== '') {
        var listItem = document.createElement('li');
        listItem.textContent = course;

        var removeButton = document.createElement('button');
        removeButton.innerHTML = '&times;'; // Use the "×" character for "X"
        removeButton.addEventListener('click', function () {
            removeSkill(listItem);
        });

        listItem.appendChild(removeButton);

        var classList = document.getElementById('classList');
        classList.appendChild(listItem);

        classInput.value = '';
    }
}

function removeSkill(classItem) {
    var classList = document.getElementById('classList');
    classList.removeChild(classItem);
}

document.querySelector("#addClassBtn").addEventListener("click", addClass);