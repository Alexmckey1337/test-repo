	/*
	function AddNewUser(){

				var username = document.querySelector("input[name='emplyee_login']").value;
				var user = document.querySelector("input[name='emplyee_name']").value;
				var email = document.querySelector("input[name='emplyee_mail']").value;
				var first_name = document.querySelector("input[name='emplyee_name']").value;
				var last_name = document.querySelector("input[name='emplyee_surname']").value;
				var middle_name = document.querySelector("input[name='emplyee_patronymic']").value;
				var phone_number = document.querySelector("input[name='emplyee_tel']").value;
				var checked = document.querySelector(".emplyee-middle span.active");
				if(!checked){
					showPopup('Выберите подразделение куда будет добавлен пользователь');
					return
				}
				if(!email || !username || !user || !first_name || !last_name || !middle_name || !phone_number ){
					showPopup('Заполните пустые поля');
					return
				}
				var hierarchy = checked.getAttribute('data-url-hierachy');
				var hierarchy_id = checked.getAttribute('data-id-department');
				var department = checked.getAttribute('data-url-department');
				var department_id = department.split('/');
				department_id = department_id[department_id.length-2];
				var master = document.querySelector(".sandwich-wrap").getAttribute('data-master') || "http://5.101.121.49:8002/api/users/1/"
				var id = document.getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
				//var isAdmin = document.getElementById('admin-chek').checked
				var data = {
					"username": username,
					"email": email,
					"first_name": first_name,
					"last_name": last_name,
					"middle_name": middle_name,
					"is_active": true,
					"is_staff": true,
					"phone_number":phone_number,
				   "department": department_id,
					"hierarchy":hierarchy_id,
					"master": id,
					"disciples": [],
					"fullname": 1,
				}

				var json = JSON.stringify(data);
				ajaxRequest('http://5.101.121.49:8002/api/create_user/', json, function(data){
					showPopup(data.message);
					[].forEach.call(document.querySelectorAll(".emplyee-left input:not([type='button']"), function(el){
									el.value = '';
							  });
				}, 'POST', true, {'Content-Type' :'application/json'});
			
			}
*/
			function createEmplyee_Hierarchy_List(){
				var departments;
				var hierarchy;
				ajaxRequest('http://5.101.121.49:8002/api/departments/', null, function(departments){ 
					departments = departments.results;
					ajaxRequest('http://5.101.121.49:8002/api/hierarchy/', null, function(hierarchy){
						hierarchy = hierarchy.results;
						Emplyee_Hierarchy_List(departments, hierarchy);

						//event click for checkbox
						var checkboxs = document.querySelectorAll('.emplyee-middle .checkbox');
						for(var j = 0;j < checkboxs.length; j++){
								checkboxs[j].addEventListener('click', function(){

									for(var m = 0; m < checkboxs.length; m++ ){
										checkboxs[m].classList.remove('active');
									}
									this.classList.add('active');
									var id =  this.getAttribute('data-id-department');
									var level = this.getAttribute('data-level-hierarchy');
									Hierarchy_path_refresh(id, level);
								})
						}
						document.querySelector('.emplyee_pop .green-button').addEventListener('click', function(){
							var department_name  = document.querySelector('.emplyee_pop input').value;
							if(department_name.length && department_name){
								 AddNewDepartment(department_name);
								 document.querySelector('.emplyee_pop input').value = '';
							}
						})
					})
				});
		}

		 function Emplyee_Hierarchy_List(departments, hierarchy){
			var html = '<table>';
			for(var i=0; i < departments.length + 1; i++){

				html +=  '<tr>';
				for(var j=0; j < hierarchy.length+1; j++){
						if( i == 0 ){
							if( j == 0 ){
								html +='<td>Отдел</td>';
							}else{
								html += '<td  data-url='+ hierarchy[j-1]['url']   +'>'+ hierarchy[j-1]['title'] +'</td>';
							}
						 }else{
							if( j == 0 ){
								html +='<td  data-url='+ departments[i-1]['url']   +'>'+ departments[i-1]['title'] +'</td>';
							}
							else{
								html +='<td><span class="checkbox" data-url-hierachy="'+
								 hierarchy[j-1]['url'] +'" data-url-department="'+ departments[i-1]['url']  +'"' +
								 '" data-id-department="'+ departments[i-1]['id'] + '"' +
								 '" data-level-hierarchy="'+ hierarchy[j-1]['level']
								  +'"></span></td>';
							}
						 }
				}
				html +=  '</tr>';
			}
			html += '</table>';
			html += '<span class="add-button">Добавить отдел</span><div class="emplyee_pop"><input type="text" placeholder="Добавить отдел" ><span class="green-button">Добавить</span></div>'
			document.getElementsByClassName('emplyee-middle')[0].innerHTML = html;
		 }

		 function AddNewDepartment(title){

			var json = JSON.stringify( {"title":title});
			ajaxRequest('http://5.101.121.49:8002/api/add_department/', json, function(data){
				createEmplyee_Hierarchy_List();
				showPopup(data.message)
			}, 'POST', true, {'Content-Type' :'application/json'});

		 }

		 function Hierarchy_path_refresh(level,id){
			var path = 'http://5.101.121.49:8002/api/users/?hierarchy__level='+level +'&department=' + id;

			ajaxRequest(path,null,function(data){
				var data = data.results;
				var html = '';
				for( var i = 0; i < data.length; i++){
				   var fullname = data[i].fullname;
				   var master = data[i].master;
				   var id = data[i].id;
				   html += '<li data-master ="'+ master +'" data-id ="'+ id +'" ><span>'+ fullname +'</span></li>'
				}
				document.querySelector(".sandwich-block ul").innerHTML = html;
			})
		 }

		 $(function(){
			createEmplyee_Hierarchy_List();

			$("#datepicker").datepicker({dateFormat: "yy-mm-dd",onSelect:function(data,t){
					//console.log('onSelect')
			}}).datepicker("setDate", new Date('1980-01-01'));
		 });



//Your validation
/*
$(':file').change(function(){
    var file = this.files[0];
    var name = file.name;
    var size = file.size;
    var type = file.type;
    
});
*/

function AddNewUser(){
    var formData = new FormData($("form[name='registry']")[0]);
    $.ajax({
        url: 'http://5.101.121.49:8002/api/create_user/',  //Server script to process data
        type: 'POST',
        xhr: function() {  // Custom XMLHttpRequest
            var myXhr = $.ajaxSettings.xhr();
            if(myXhr.upload){ // Check if upload property exists
               // myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
            }
            return myXhr;
        },
        //Ajax events
       // beforeSend: beforeSendHandler,
        success: completeHandler,
        error: errorHandler,
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });
}

function progressHandlingFunction(e){
    if(e.lengthComputable){
        $('progress').attr({value:e.loaded,max:e.total});
    }
}

function completeHandler(data){
  console.log('finish');
  console.log(data);
}
function errorHandler(){
  console.log('error');
}