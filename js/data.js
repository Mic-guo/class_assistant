document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        addClass();
    }
});

function addClass() {
    var classInput = document.getElementById('classInput');
    var course = classInput.value.trim();
    var classList = document.getElementById('classList');
    var listItem = document.createElement('li');
    listItem.textContent = course;

    // check if course already exists in classList
    var exists = Array.from(classList.getElementsByTagName('li')).some((li) => li.textContent.trim().slice(0, -1) === course);

    if (course !== '' && !exists) {
        var removeButton = document.createElement('button');
        removeButton.innerHTML = '&times;'; // Use the "×" character for "X"
        removeButton.addEventListener('click', function () {
            removeSkill(listItem);
        });

        listItem.appendChild(removeButton);
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

        listItems.appendChild(document.createTextNode("The prerequisites for " + prereqs + " are [XYZ]. You have completed [XYZ]. You still need to complete [XYZ]."));
        listItems.appendChild(document.createElement('br'));
        listItems.appendChild(document.createTextNode("Grade Distribution: "));
        listItems.appendChild(document.createElement('br'));
        listItems.appendChild(document.createTextNode("Exams: "));
        listItems.appendChild(document.createElement('br'));
        listItems.appendChild(document.createTextNode("Workload: "));

        var prereqList = document.getElementById('prereqList');
        prereqList.appendChild(listItems);

        prereqInput.value = '';
    }
}
document.querySelector("#addPrereqBtn").addEventListener("click", prereqData);