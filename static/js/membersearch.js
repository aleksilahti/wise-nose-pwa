function handleSearchMember() {
    let data = getInputData();

    fetch("/exportmembers", {
        method: "POST",
        body: JSON.stringify(data)
    })
    .then((response) => {
        if (response.url) {
            window.location.href = response.url;
        }
    })
}

function downloadMemberData() {
    let data = getInputData();

    fetch("/exportmembers/search", {
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
    let person_name = document.getElementById("person_name").value;
    let role = document.getElementById("role").value;
    let wise_nose_id = document.getElementById("wise-nose-id").value;

//    let role_select = document.getElementById("role");
//    let trainer_name = trainer_select.options[role_select.selectedIndex].text;

    return {"person_name": person_name, "role": role, "wise_nose_id": wise_nose_id};
}