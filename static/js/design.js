// background overlay when sidebar-menu displayed
$(".navbar-toggler").on("click", function () {
     $(this).toggleClass("mask")
})

//active link
$('a[href$="'+url_path+'"]').parent().addClass("active")

//clicked dog container
$(".dog-container").on("click", function(e){
     if($(e.target).hasClass("btn") == false && $(e.target).hasClass("fas") == false){ // prevent the click to be executed on the button inside dog cards
          if($(this).hasClass("expanded")){
               $(this).removeClass("expanded")
          }else{
               $(".expanded").removeClass("expanded")
               $(this).addClass("expanded")
          }
     }
})


$("#number_of_samples").on("input", function(){
     let nbr_samples = parseInt($(this).val())
     $(".samples").empty()
     for(i = 0 ; i< nbr_samples; i++){
          $(".samples").append("<div class='sample'><p>"+(i+1)+"</p><div class='sample-box bg-not-hot'></div></div>")
     }
     if(nbr_samples < 9){
          $(".samples").append("<div class='sample'><div class='sample-box add'><i class='fas fa-plus fa-lg'></i></div></div>")
     }

     $(".sample-box.add").on("click", function(){
          if(nbr_samples < 9){
               nbr_samples += 1
               $("#number_of_samples").val(nbr_samples)
               $(".sample").not(":last-child").last().after("<div class='sample'><p>"+(nbr_samples)+"</p><div class='sample-box bg-not-hot'></div></div>")
               $(".sample").not(":last-child").last().children().on("click", function(){
                    if($(this).hasClass("bg-hot")){
                         $(this).removeClass("bg-hot")
                         $(this).addClass("bg-not-hot")
                    }else{
                         $(this).removeClass("bg-not-hot")
                         $(this).addClass("bg-hot")
                    }
               })
          }
          if(nbr_samples == 9){
               $(".sample-box.add").remove()
          }
     })

     sample_box_listener()
})

function sample_box_listener(){
     $(".sample-box").on("click", function(){
          if($(this).hasClass("bg-hot")){
               $(this).removeClass("bg-hot")
               $(this).addClass("bg-not-hot")
          }else{
               $(this).removeClass("bg-not-hot")
               $(this).addClass("bg-hot")
          }
     })
}