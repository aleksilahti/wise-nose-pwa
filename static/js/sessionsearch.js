function handleSearchSession() {
    let data = getInputData();

    fetch("/exportsessions", {
        method: "POST",
        body: JSON.stringify(data)
    })
    .then((response) => {
        if (response.url) {
            window.location.href = response.url;
        }
    })
}

function downloadSessionData() {
    let data = getInputData();

    fetch("/exportsessions/search", {
        method: "POST",
        body: JSON.stringify(data)
    })
    .then((response) => {
        if (response.url) {
            window.location.href = response.url;
        }
    })
}

function getInputData() {
    let start_date = document.getElementById("start_date").value;
    let end_date = document.getElementById("end_date").value;

    let supervisor_select = document.getElementById("supervisor");
    let supervisor_name = supervisor_select.options[supervisor_select.selectedIndex].text;

    let dog_select = document.getElementById("dog");
    let dog_name = dog_select.options[dog_select.selectedIndex].text;

    return {"start_date": start_date, "end_date": end_date, "supervisor_name":supervisor_name, "dog_name": dog_name};
}