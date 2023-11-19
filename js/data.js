// Function to update the visibility of classContainer
function updateClassContainerVisibility() {
    var classContainer = document.getElementById('classContainer');
    var classList = document.getElementById('classList');
    var next = document.getElementById('next')
    classContainer.style.display = classList.hasChildNodes() ? 'block' : 'none';
    next.style.visibility = classList.hasChildNodes() ? 'visible' : 'hidden';

}

// Observer configuration
var observerConfig = { childList: true };

// Callback function to be called when mutations are observed
var mutationCallback = function (mutationsList) {
    for (var mutation of mutationsList) {
        if (mutation.type === 'childList') {
            // Update the visibility of classContainer on any change in child nodes
            updateClassContainerVisibility();
            break;
        }
    }
};

// Create a new observer with the callback and configuration
var observer = new MutationObserver(mutationCallback);

// Start observing the classList for changes
observer.observe(document.getElementById('classList'), observerConfig);
updateClassContainerVisibility();

document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        // Check if the active element is the classInput field
        if (document.activeElement === document.getElementById('classInput')) {
            addClass();
        }
        // Check if the active element is the prereqInput field
        else if (document.activeElement === document.getElementById('prereqInput')) {
            getPrereqData();
        }
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

// document.querySelector("#addClassBtn").addEventListener("click", addClass);

function getPrereqData() {
    var prereqInput = document.getElementById('prereqInput');
    var prereqs = prereqInput.value.trim();

    if (prereqs !== '') {
        // Assume you have a server endpoint like "/get_todo_courses"
        var url = "/get_prereq/";

        // You need to replace this with the actual completed_courses_str value
        var completedCoursesStr = "EECS 280, EECS 183";

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                desired_course_str: prereqs,
                completed_courses_str: completedCoursesStr,
            }),
        })
        .then(response => response.json())
        .then(todoCourses => {
            // Use the todoCourses data as needed
            updatePrereqList(todoCourses);
        })
        .catch(error => console.error('Error:', error));

        prereqInput.value = '';
    }
}

function updatePrereqList(todoCourses) {
    var prereqList = document.getElementById('prereqList');
    prereqList.innerHTML = '';

    var listItems = document.createElement('li');
    // Assuming todoCourses is an array of course codes
    listItems.appendChild(document.createTextNode("The prerequisites for " + prereqs + " are " + todoCourses.join(', ') + "."));

    // Add more code to update the list with additional information

    prereqList.appendChild(listItems);
}

document.querySelector("#addPrereqBtn").addEventListener("click", getPrereqData);

// function prereqData() {
//     var prereqInput = document.getElementById('prereqInput');
//     var prereqs = prereqInput.value.trim();

//     if (prereqs !== '') {
        
//         var prereqList = document.getElementById('prereqList');

//         prereqList.innerHTML = '';
//         var listItems = document.createElement('li');

//         listItems.appendChild(document.createTextNode("The prerequisites for " + prereqs + " are [XYZ]. You have completed [XYZ]. You still need to complete [XYZ]."));
//         listItems.appendChild(document.createElement('br'));
//         listItems.appendChild(document.createTextNode("Grade Distribution: "));
//         listItems.appendChild(document.createElement('br'));
//         listItems.appendChild(document.createTextNode("Exams: "));
//         listItems.appendChild(document.createElement('br'));
//         listItems.appendChild(document.createTextNode("Workload: "));

//         var prereqList = document.getElementById('prereqList');
//         prereqList.appendChild(listItems);

//         prereqInput.value = '';
//     }
// }

const btn = document.getElementById('next');
const pixels = window.innerHeight + 1000;

btn.addEventListener('click', () => {
  window.scrollBy({
    top: pixels,
    behavior: 'smooth' 
  });
});