$(".navbar-toggler").on("click", function () {
     $(this).toggleClass("mask")
});
console.log(url_path)
$('a[href$="'+url_path+'"]').parent().addClass("active")