function handleSearchDog(url) {
    let data = getInputData();

    fetch(url, {
        method: "POST",
        body: JSON.stringify(data)
    })
    .then((response) => {
        if (response.url) {
            window.location.href = response.url;
        }
    })
}

function downloadDogsData(url) {
    let data = getInputData();

    fetch(url, {
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
    let dog_name = document.getElementById("dog-name").value;
    let age = document.getElementById("age").value;
    let wise_nose_id = document.getElementById("wise-nose-id").value;

    let trainer_select = document.getElementById("trainer-name");
    let trainer_name = trainer_select.options[trainer_select.selectedIndex].text;

    return {"dog_name": dog_name, "age": age, "wise_nose_id": wise_nose_id, "trainer_name": trainer_name};
}