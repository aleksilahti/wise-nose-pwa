function handleSearchClick() {
    let search_value = document.getElementById("search").value;
    let event = new CustomEvent('do_search', {'detail': search_value});
    window.dispatchEvent(event);
}