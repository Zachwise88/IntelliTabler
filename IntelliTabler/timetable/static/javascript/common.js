const modal = new bootstrap.Modal(document.getElementById("addFormModal"));
var cData ={};
var activePage;
// $(document).on("click", ".childButtons", function(){
//     if($(this).hasClass("childButtons")){
//         $(".childButtons").removeClass("active");
//     }
//     else{
//         $("button").not(".parentButtons").not(".childButtons").removeClass("active");
//     }
    
//     $(this).addClass("active");
// })

htmx.on("htmx:afterSwap", (e) => {
    console.log(e.detail.pathInfo.requestPath.split('/')[1]);
    if(e.detail.target.id=="displayChild"){
        $('#displayChild').collapse('show');
        htmx.config.defaultSwapDelay=0;
    }
    if(e.detail.target.id=="sidebarBody"){
        $("#offsetToggle").collapse('show');
        htmx.config.defaultSwapDelay=0;
    }
    if(e.detail.target.id=="mainContent"){
        $('#offcanvasSidebar').offcanvas('hide');
        // $('#mainContent').collapse('show');
        // htmx.config.defaultSwapDelay=0;
    }
    if(e.detail.target.id=="listObjects"){
        let pWidth = 0;
        listSidebar= document.getElementById("listObjectsDiv")
        
        const tempObserver = new ResizeObserver(entries => {
          for (const entry of entries) {
            const width = entry.borderBoxSize?.[0].inlineSize;
            if (typeof width === 'number' && width !== pWidth) {
              pWidth = width;
              $("#displayChild").css("margin-left", width+'px');
            }
          }
        });
        
        tempObserver.observe(listSidebar);
    }

    //AfterSwap for Modal Handeler
    if(e.detail.target.id == "addForm") {
        test=e.detail.pathInfo.requestPath.split('/')[1];
        if(test=="addPreferences"){
            setGroupChoice();
        }
        //Enables Tooltips
        enableTooltips();

        modal.show();
    }
    
})

function enableTooltips(){
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}


htmx.on("htmx:beforeSwap", (e) => {

    if(e.detail.target.id=="displayChild" && !$(e.detail.target).hasClass('htmx-request') && e.detail.requestConfig.verb!="delete"){
        if($('#displayChild').hasClass('show')){
            htmx.config.defaultSwapDelay=500;
        }
        $('#displayChild').collapse('hide');

    }
    // if(e.detail.target.id=="mainContent"){
    //     if($('#mainContent').hasClass('show')){
    //         htmx.config.defaultSwapDelay=500;
    //     }
    //     $("#mainContent").collapse('hide');
    // }
    if(e.detail.target.id=="sidebarBody"){
        $("#mainContent").html("");
    }

    //Handles Modal hiding
    if (e.detail.target.id == "addForm" && !e.detail.xhr.response){
        modal.hide();
        e.detail.shouldSwap = false;
    }

    if(cData.calendarDiv && e.target.id=="mainContent"){
        cleanupCalendar();
    }
})

htmx.on('htmx:beforeSend', (e) => {
    if(($(e.target).hasClass('yearItem'))){
        $("#departmentSelect").text($(e.target).closest('.depDropDown').find('.depItem').text().split(" ")[0]+" " +$(e.target).text());
        $("#offcanvasLabel").text($(e.target).closest('.depDropDown').find('.depItem').text().split(" ")[0]+" " +$(e.target).text());
    }
    if($(e.target).hasClass('childButtons')){
        if($(e.target).hasClass('moduleButtons')){
            $("#displayChild").attr("hx-get", "/getModules/"+e.target.id.split('.')[0]+"/"+currentTimetable);

        }else{
            $("#displayChild").attr("hx-get", "/getTeacher/"+e.target.id.split('.')[0]+"/"+currentTimetable);
        }
        htmx.process(htmx.find("#displayChild"));
    }
    if($(e.target).hasClass('event')){
        $("#modalBody").attr("hx-get", "/getModules/"+e.target.id+"?calendar=1");
        htmx.process(htmx.find("#modalBody"));
    }
})

function cleanupCalendar(){
    $(document).off("addEvent");
    
    $(document).off("periodUpdate");
    
    $(document).off("updateColor");
    delete dataModal;
    $(cData.calendarDiv).off();
    for(var k in cData){
        delete cData[k];
    }
    console.log(cData);
}

htmx.on("hidden.bs.modal", () => {
    $("#addForm").html("");
});

$(document).on("click", ".parentButtons, .childButtons", function(){
    if($(this).hasClass("childButtons")){
        clickedChild=this.id.split('.')[0]
    }else{
        clicked=this.id.split('.')[0];
    }
    
    });

$(document).on('departmentChange yearChange', function(){
    location.reload();
})

function getClicked(){
    return clicked;
}

function getChild(){
    return clickedChild;
}

$(document).on("click", ".sidebar-link", function(){
    activePage=this.id;
    $(".sidebar-link").parent().removeClass("border-bottom");
    $(this).parent().addClass("border-bottom");
})

let prevWidth = 0;
sidebar= document.getElementById("sidebar")

const sidebarObserver = new ResizeObserver(entries => {
  for (const entry of entries) {
    const width = entry.borderBoxSize?.[0].inlineSize;
    if (typeof width === 'number' && width !== prevWidth) {
      prevWidth = width;
      $("#contentCol").css("margin-left", width+'px');
    }
  }
});

sidebarObserver.observe(sidebar);

function getTextColor(color){
    rgb=color.split('#')[1].match(/.{1,2}/g);
    r=parseInt(rgb[0], 16);
    g=parseInt(rgb[1], 16);
    b=parseInt(rgb[2], 16);
    if ((r*0.299 + g*0.587 + b*0.114) > 150) {
        return '#000000'
     }else{
        return '#ffffff';
     }
}

$(document).on('click', '#infoBtnGroup button', function(){
    $("#teacherInfoCont .collapse").collapse('hide');
})

$(document).on('TeacherDeleted', function(e){
    $("#displayChild").html('');
});

$(document).on("click", ".rotateLink", function(){
    $(this).children("i").toggleClass("down"); 
});

$(document).on("change", "#parentChoice", function(){
    setGroupChoice();
    
})

$(document).on("change", "#groupChoice", function(){
    setModuleChoice();

})

function setGroupChoice(){
    
    $.get('/getGroups/' + $("#parentChoice").val(), function(data){
        $('#groupChoice').empty()
        var options=''
        data.choices.forEach(element => {
            options+= '<option value="' + element[0] +'">' + element[1] +'</option>';
        });
        $('#groupChoice').html(options);
        $('#groupChoice').prop('disabled',false)

        setModuleChoice();
    })
}
function setModuleChoice(){
    $.get('/getModulesJson/' + $('#groupChoice').val(), function(data){
        $('#moduleChoice').empty()
        var options=''
        data.choices.forEach(element => {
            options+= '<option value="' + element[0] +'">' + element[1] +'</option>';
        });
        $('#moduleChoice').html(options);
        $('#moduleChoice').prop('disabled',false)
    })
}

