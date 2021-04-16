
$(document).ready(function(){
     // background overlay when sidebar-menu displayed
     $(".navbar-toggler").on("click", function () {
          $(this).toggleClass("mask")
          $(".search").toggleClass("none")
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

     // create the number of boxes according the number from the input #number_of_samples
     $("#number_of_samples").on("input", function(){
          var nbr_samples = 0
          if((parseInt($(this).val()) < 10 && parseInt($(this).val()) >=0) || ($(this).val() == "")){
               nbr_samples = parseInt($(this).val())
          }else{
               $(this).val(0)
          }
          $(".samples").empty()
          for(i = 0 ; i< nbr_samples; i++){
               $(".samples").append("<div class='sample_and_search'><div class='sample'><p>"+(i+1)+"</p><div class='sample-box bg-not-hot'></div></div>  <div class='wise_nose_id'><input type='text' placeholder='ID' autocomplete='off' class='wise_nose_id_search'/></div></div>")
          }
          if(nbr_samples < 9){
               $(".samples").append("<div class='sample'><div class='sample-box add'><i class='fas fa-plus fa-lg'></i></div></div>")
          }
          $(".wise_nose_id_search").on("input", search)
          $(".sample-box.add").on("click", function(){
               if(nbr_samples < 9){
                    nbr_samples += 1
                    $("#number_of_samples").val(nbr_samples)
                    $(".sample_and_search").not(":last-child").last().after("<div class='sample_and_search'><div class='sample'><p>"+nbr_samples+"</p><div class='sample-box bg-not-hot'></div></div>  <div class='wise_nose_id'><input type='text' placeholder='ID' autocomplete='off' class='wise_nose_id_search'/></div></div>")
                    $(".wise_nose_id_search").on("input", search)
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

          $(".sample-box").on("click", function(){
               if($(this).hasClass("bg-hot")){
                    $(this).removeClass("bg-hot")
                    $(this).addClass("bg-not-hot")
               }else{
                    $(this).removeClass("bg-not-hot")
                    $(this).addClass("bg-hot")
               }
          })
     })
     let order = 1

     //initalize samples when edit session
     $("#number_of_samples").trigger("input")
     if (typeof samp !== 'undefined'){
          for([key, item] of Object.entries(samp)){
               sampleList = $(".sample-box").not(".add")
               sampleIDList = $(".wise_nose_id_search")
               if(item.is_hot == 1){
                    $(sampleList[key]).removeClass("bg-not-hot")
                    $(sampleList[key]).addClass("bg-hot")
               }
               $(sampleIDList[key]).val(item.wise_nose_id)
          }
     }

     //initalize samples when executing session
     if (typeof dog_answer !== 'undefined'){
          sampleList = $(".sample .outlined")
          for([key, item] of Object.entries(dog_answer)){
               childrens = $(sampleList[key-1]).children().not('.add')
               for(i=0; i<item['order'].length-1; i++){
                    childrens.last().after("<div class='sample-box bg-not-hot'><p class='order'></p><p class='active'>-</p></div>")
               }
               childrens = $(sampleList[key-1]).children().not('.add')
               childrens.toArray().forEach(function(_, idx){
                    if(item["order"].length != 0){
                         switch (item["order"][idx][0]){
                              case 1: 
                                   $(childrens[idx]).removeClass("bg-not-hot")
                                   $(childrens[idx]).addClass("bg-interested")
                                   break;
                              case 2:
                                   $(childrens[idx]).removeClass("bg-not-hot")
                                   $(childrens[idx]).addClass("bg-maybe")
                                   break;
                              case 3:
                                   $(childrens[idx]).removeClass("bg-not-hot")
                                   $(childrens[idx]).addClass("bg-hot")
                                   break;
                         }
                         $($(childrens[idx]).children()[1]).on("click", function(e){
                              e.stopPropagation()
                              $(this).parent().remove()
                              order -= 1
                              $(".popup").removeClass("active")
                         })
                         if(item["order"][idx][1] != -1){
                              $($(childrens[idx]).children()[0]).text(item["order"][idx][1])
                              order += 1
                         }
                    }
               })
          }
     }

     //execute session logic
     $(".sample-box").not(":last-child").on("click", function(e){
          e.stopPropagation()
          $(".sample-box.active").removeClass("active")
          $(".popup").addClass("active")
          $(this).addClass("active")
          sample = $(this)
          if(sample.children().text() ==""){
               $("#order").val(order)
          }else{
               $("#order").val($(sample.children()[0]).text())
          }
     })
     $(".sample-box.not-outlined").on("click", function(){
          if ($(this).is("#no")){
               sample.removeClass()
               sample.addClass("sample-box bg-not-hot")
          }else if ($(this).is("#interested")){
               sample.removeClass()
               sample.addClass("sample-box bg-interested")
          }else if ($(this).is("#maybe")){
               sample.removeClass()
               sample.addClass("sample-box bg-maybe")
          }else{
               sample.removeClass()
               sample.addClass("sample-box bg-hot")
          }
          if(sample.children().first().text() == ""){
               order += 1
          }
          sample.children().first().text($("#order").val())
          $(".popup").removeClass("active")
          sample.removeClass("active")
     })

     $(document).on("click", function(e){
          var $target = $(e.target);
          if(!$target.closest('.popup').length && $('.popup').hasClass("active")) { //detect click outside the .popup div
               $(".popup").removeClass("active")
               $(".sample-box.active").removeClass("active")
          }
          if(!$target.closest('.wise_nose_id_search').length && !$target.closest('.wise_nose_id_answers').length) { //detect click outside the search field or answers
               $(".wise_nose_id ul.wise_nose_id_answers").remove()
          }
     })

     $(".sample-box.add").on("click", function(){
          $(this).parent().children().not(":last-child").last().after("<div class='sample-box bg-not-hot'><p class='order'></p><p class='active'>-</p></div>")
          $(this).parent().children().not(":last-child").last().on("click", function(e){
               e.stopPropagation()
               $(".sample-box.active").removeClass("active")
               $(".popup").addClass("active")
               $(this).addClass("active")
               sample = $(this)
               if($(sample.children().first()).text() ==""){
                    $("#order").val(order)
               }else{
                    $("#order").val($(sample.children().first()).text())
               }
          })
          $(this).parent().children().not(":last-child").last().children().last().on("click", function(e){
               e.stopPropagation()
               $(this).parent().remove()
               order -= 1
               $(".popup").removeClass("active")
          })
     })

     $("#minus").on("click", function(){
          val = $("#order").val()
          if(val > 1){
               $("#order").val(val-1)
          }
     })

     $("#add").on("click", function(){
          val = parseInt($("#order").val())
          $("#order").val(val + 1)
     })

     $("#previous").on("click", function(){
          actualSelectedSample = $(".sample-box.active")
          allSamples = $(".sample-box").not(":last-child")
          if(allSamples.index(actualSelectedSample) != 0){
               actualSelectedSample.removeClass("active")
               newSample = $(allSamples[allSamples.index(actualSelectedSample)-1]).addClass("active")
               if(newSample.text() == ""){
                    $("#order").val(order)
               }else{
                    $("#order").val(newSample.text())
               }
               newSample.trigger("click")
          }
     })

     $("#next").on("click", function(){
          actualSelectedSample = $(".sample-box.active")
          allSamples = $(".sample-box").not(":last-child")
          if(allSamples.index(actualSelectedSample) != allSamples.length-1){
               actualSelectedSample.removeClass("active")
               newSample = $(allSamples[allSamples.index(actualSelectedSample)+1]).addClass("active")
               if(newSample.text() == ""){
                    $("#order").val(order)
               }else{
                    $("#order").val(newSample.text())
               }
               newSample.trigger("click")
          }
     })

     //search wise nose id samples 

     function search(){
          input =$(this) 
          //$(".wise_nose_id ul.wise_nose_id_answers").children().remove()
          if(input.val() == ""){
               $(".wise_nose_id ul.wise_nose_id_answers").remove()
          }else{
               $.post("/samples/"+input.val()).done(function(result){
                    $(".wise_nose_id ul.wise_nose_id_answers").children().remove()
                    result = JSON.parse(result)
                    if(input.val().length == 1){
                         input.parent().append("<ul class='wise_nose_id_answers'></ul>")
                    }
                    if(result.length != 0){
                         result.forEach(function(_, index){
                              Object.keys(result[index]).forEach(function(key) {
                                   input.parent().children().last().append("<li>"+key+"</li>") //add to ul element 
                               });
                         })
                         li_samples_wise_nose_id = input.parent().children().last().children().toArray()
                         li_samples_wise_nose_id.forEach(function(_,index){
                              $(li_samples_wise_nose_id[index]).on("click", function(){
                                   li_element = $(this)
                                   input.val($(this).text())
                                   $(".wise_nose_id ul.wise_nose_id_answers").remove()
                                   result.forEach(function(_, index){
                                        Object.keys(result[index]).forEach(function(key) {
                                             if(key == li_element.text()){
                                                  sample_box = input.parent().parent().children().first().children().last() // sample box linked to the li_element
                                                  sample_box.removeClass()
                                                  if(result[index][key] == 0){
                                                       sample_box.addClass("sample-box bg-not-hot")
                                                  }else{
                                                       sample_box.addClass("sample-box bg-hot")
                                                  }
                                             }
                                         });
                                   })
                              })
                         })
                    }else{
                         $(".wise_nose_id ul.wise_nose_id_answers").remove()
                    }
               })
          }
     }
})

// js form for the session edit page
function save(id){
     var samples = [] // false --> not hot / true --> hot
     var samples_wise_id = []
     $(".sample").toArray().forEach(function(_, index){
          if(!$($(".sample").toArray()[index].children).hasClass("add")){
               if($($(".sample").toArray()[index].children).hasClass("bg-not-hot")){
                    samples.push(false)
               }else{
                    samples.push(true)
               }
               samples_wise_id.push($($(".wise_nose_id_search").toArray()[index]).val())
          }
     });
     $.post("/sessions/edit/"+id, 
     {    
          "date": $("#date").val(),
          "dog": $("#dog").val(),
          "supervisor": $("#supervisor").val(),
          "number_of_samples": $("#number_of_samples").val(),
          "samples": samples,
          "samples_wise_id": samples_wise_id
     }).done(function(){
          window.location.replace("/sessions")
     })
}

//js form for the session execute page
function save_execute(id){
     var samples = []
     actualBoxes = $(".sample .outlined").toArray()
     actualBoxes.forEach(function(_, index){
          childrens = $(actualBoxes[index]).children()
          samples.push([])
          childrens.toArray().forEach(function(_, child_index){
               if(!$(childrens[child_index]).hasClass("add")){
                    if($(childrens[child_index]).hasClass("bg-not-hot")){ //not-hot = 0, interested = 1, maybe=2, yes = 3
                         samples[index].push([0, $($(childrens[child_index]).children()[0]).text()])
                    }else if($(childrens[child_index]).hasClass("bg-interested")){
                         samples[index].push([1, $($(childrens[child_index]).children()[0]).text()])
                    }else if ($(childrens[child_index]).hasClass("bg-maybe")){
                         samples[index].push([2, $($(childrens[child_index]).children()[0]).text()])
                    }else{
                         samples[index].push([3, $($(childrens[child_index]).children()[0]).text()])
                    }
               }
          })
     })
     $.ajax({
          url: "/sessions/execute/"+id,
          type: 'POST',
          data: JSON.stringify({samples}),
          contentType: 'application/json; charset=utf-8',
          async: false
     }).done(function(){
          window.location.replace("/sessions")
     })
}