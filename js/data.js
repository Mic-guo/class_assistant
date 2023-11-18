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



function prereqData() {
    var prereqInput = document.getElementById('prereqInput');
    var prereqs = prereqInput.value.trim();

    if (prereqs !== '') {
        
        var prereqList = document.getElementById('prereqList');

        prereqList.innerHTML = '';
        var listItems = document.createElement('li');
        listItems.textContent = "The prerequisites for " + prereqs + " are [XYZ]. You have completed [XYZ]. You still need to complete [XYZ].";

        var prereqList = document.getElementById('prereqList');
        prereqList.appendChild(listItems);

        prereqInput.value = '';
    }
}
document.querySelector("#addPrereqBtn").addEventListener("click", prereqData);