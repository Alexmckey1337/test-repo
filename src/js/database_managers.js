import 'jquery'


$(document).ready(function(){
    const path = window.location.href.split('/')[2];
    $("#hg-table").hide();
    
    $.ajax({
        url:"http://"+path+"/api/managers"  // TODO:добавить работу по динамическому адресу
    }).then(function(data){
        var count = data.count;
        
        //$("<p> Всего "+count+" записей</p>").insertBefore("#managers");

        for(var i=0;i<count;i++){
        
        $("<tr><td>"+data.result[i].person.fullname+"</td></tr>").insertAfter("#manager-row");//.attr("data-id",i);
        
        }
       

       //onclick function for showing assigned homegroups for clicked manager
$('#managers').on("click","td",function(){
  
$("tr .selected").removeClass("selected")
$(this).addClass("selected")
$(".hg-row").remove()
$("#hg-table").show();


    

var search=($(this).text());
for(var i = 0;i<count;i++){
    if(data.result[i].person.fullname==search){
       $("<tr class=hg-row><td>"+data.result[i].group.title+"</td></tr>").insertAfter("#hg-head");
        
       
    }
}
    })
    removeDuplicateRows($('table'));  
    })

function removeDuplicateRows($table){
function getVisibleRowText($row){
return $row.find('td:visible').text().toLowerCase();
}

$table.find('tr').each(function(index, row){
var $row = $(row);
$row.nextAll('tr').each(function(index, next){
    var $next = $(next);
    if(getVisibleRowText($next) == getVisibleRowText($row))
        $next.remove();
})
});
}
})