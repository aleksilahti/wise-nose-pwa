// background overlay when sidebar-menu displayed
$(".navbar-toggler").on("click", function () {
     $(this).toggleClass("mask")
})

//active link
$('a[href$="'+url_path+'"]').parent().addClass("active")

//clicked dog container
$(".dog-container").on("click", function(){
     if($(this).hasClass("expanded")){
          $(this).removeClass("expanded")
     }else{
          $(".expanded").removeClass("expanded")
          $(this).addClass("expanded")
     }
})