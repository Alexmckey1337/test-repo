$(document).ready(function() {
    //Коли  push  нада перевіряти key
   
      document.querySelector('.turn').addEventListener('click', function(){
         
         // this.innerHTML = this.innerHTML =='Свернуть таблицу' ? 'Полная таблица': 'Свернуть таблицу'

         if(   this.innerHTML =='Свернуть таблицу'  ){
              this.innerHTML = 'Полная таблица'
             getWeekShortReports('api/v1.0/week_reports/', 'report_week');
         }else{
              this.innerHTML = 'Свернуть таблицу'
             getWeekReports('api/v1.0/week_reports/', 'report_week');
         }

      })
})


function init_report(){
	window.my_id = config.user_id; // for test my_id =2 
    getWeekReports('api/v1.0/week_reports/', 'report_week', function () {
        getReports('api/v1.0/month_reports/', 'report_mounth', function () {
            getReports('api/v1.0/year_reports/', 'report_year', function () {
        		document.querySelector("#tab_plugin li").click();
     });
     });
  });


  

   tab_plugin();
}


function getReports(period,container,callback){
    ajaxRequest(CONFIG.DOCUMENT_ROOT + period, null, function(data) {

        let results = data.results;

        if( !results.length){
          //  showPopup('Не созданные репорты')
            return ''
        }

        window.reports_by_mid = [] //[2,120]
        for (let i = 0; i < results.length; i++) {
            let report = results[i];


            if(!reports_by_mid[report['mid']]) {
                reports_by_mid[report['mid']] = []
            }
            reports_by_mid[report['mid']].push(report)
        }


        //Берем id подчиненных на мені  

        window.sub_ids = []; //[3, 5, 6, 7, 8, 120]

        for (let j = 0; j < reports_by_mid[my_id].length; j++) {

            if( jQuery.inArray( reports_by_mid[my_id][j]['uid'], sub_ids ) == -1){
                 sub_ids.push(reports_by_mid[my_id][j]['uid'])
            } 
           
        }

        //Генерация отчетов по подчиненных 
        let wrap = ''

        if(  !reports_by_mid[my_id] ){
           //  showPopup('Не созданные репорты')
            return ''
        }


        for (let m = 0; m < sub_ids.length; m++) {
            //Постройка таблиц  ....1 sub_ids это 1 строка таблица

            let report_event_container = '' // Контейнер Снижко Ю.И.
            // получаем отчеты только на подченных если они есть 
            if(reports_by_mid[sub_ids[m]]) {


              
                window.week_reports = []
                for (let p = 0; p < reports_by_mid[sub_ids[m]].length; p++) {


                    week_reports/*[reports_by_mid[sub_ids[m]][p]['date']]*/.push(reports_by_mid[sub_ids[m]][p])

                }


                let thead = '<div class="event-wrap clearfix"><table>'


                let html = '<div class="event-wrap-scroll">'


                let report_parent_by_current_week = reports_by_mid[my_id].filter(function (el) {
                        return el.uid == sub_ids[m] /*&& week_reports[l][0] == el.date*/
                     })


                   // week_reports.unshift(report_parent_by_current_week[0])

                let caption = period == 'api/v1.0/month_reports/' ? getRussianMonth(new Date(week_reports[0]['date']).getMonth()) : new Date(week_reports[0]['date']).getFullYear()

                      html += '<table><caption>' + caption + '</caption><tr>'+
                            '<th>Д.Г.<br>к-во</th><th>Д.Г.<br>пож.</th><th>Ноч.<br>к-во</th>'+
                            '<th>Сл.<br>к-во</th><th>Сл.<br>нов.</th><th>Сл.<br>пок.</th>'+
                        '</tr>' +

    
                         '<tr uid="'+  report_parent_by_current_week[0]['uid'] +'"   mid="'+  report_parent_by_current_week[0]['mid'] +'">'+
                            '<td>'+ report_parent_by_current_week[0]['home_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['home_as_leader_value']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['night_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_coming_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_repentance_count']  +'</td>'+
                        '</tr>'


                for (let s = 0; s < week_reports.length; s++) {




                     window.thead = ''

                     
                    




                        html += '<tr>'


                    for (let prop in week_reports[s]) {

                            //console.log( week_reports[s] )

                        if( prop == 'fullname' ){
                            if(s ==0){

                                thead +=  '<caption>'+ report_parent_by_current_week[0]['fullname']   +'</caption>'+
                        '<tr>'+
                            '<th>Подчиненные</th>'+
                        '</tr>'+
                        '<tr><td>'+  report_parent_by_current_week[0]['fullname']  +'</td></tr>'
                               // console.log(  week_reports[l][s]['fullname']   )
                            }
                            thead += '<tr><td>'+  week_reports[s]['fullname']  +'</td></tr>'
                        }
                            //if(jQuery.inArray(prop, ['id', 'mid', 'uid', 'week', 'from_date', 'to_date']) != -1) continue
                            if(jQuery.inArray(prop, [ 'home_count', 'home_value', 'night_count', 'service_count', 'service_coming_count','service_repentance_count']) == -1) continue
                            html += '<td data-prop="' + prop + '" mid="' + week_reports[s]['mid']   +'" uid="' + week_reports[s]['uid']   +'">' + week_reports[s][prop] + '</td>'
                        }

                        html += '</tr>'


                       
                
                    


                   
                }
                


                  //Сумма 
                        
                        html += '<tr class="marg">'+
                            '<td></td><td></td><td></td><td></td><td></td><td></td>'+
                        '</tr>'+
                        '<tr>'+
                            '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['home_count']  +'</td>'+
                           '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['home_value']  +'</td>'+
                           '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['night_count']  +'</td>'+
                           '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['service_count']  +'</td>'+
                           '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['service_coming_count']  +'</td>'+
                           '<td uid="' + report_parent_by_current_week[0]['uid'] + '">'+ report_parent_by_current_week[0]['service_repentance_count']  +'</td>'+
                        '</tr>'
                       

                    html += '</table>'
                 thead += '<tr class="marg"><td></td>'+
                        '</tr><td>Сумма:</td></table>'
                //console.log(thead)
                  html = thead + html;
                 //  console.log(html)


                html += '</div></div>'
                report_event_container += html
                wrap += report_event_container

            }
        }

        //console.log(  new Date().getTime() )
        document.getElementById(container).innerHTML = wrap

    if(callback){
        callback()
    }



    })
}







function getWeekReports(period,container,callback){
    ajaxRequest(CONFIG.DOCUMENT_ROOT + period, null, function(data) {


        let results = data.results;


        if( !results.length){
          //  showPopup('Не созданные репорты')
            return ''
        }

        window.reports_by_mid = [] //[2,120]



        //  reports_by_mid = [ 0: [{},{}]  ]
        for (let i = 0; i < results.length; i++) {
            let report = results[i];


            if(!reports_by_mid[report['mid']]) {
                reports_by_mid[report['mid']] = []
            }
            reports_by_mid[report['mid']].push(report)
        }


        //Берем id подчиненных на мені  

        window.sub_ids = []; //[3, 5, 6, 7, 8, 120]

        if(  !reports_by_mid[my_id] ){
           //  showPopup('Не созданные репорты')
            return ''
        }

        for (let j = 0; j < reports_by_mid[my_id].length; j++) {

            if( jQuery.inArray( reports_by_mid[my_id][j]['uid'], sub_ids ) == -1){
                 sub_ids.push(reports_by_mid[my_id][j]['uid'])
            } 
           
        }


        //Генерация отчетов по подчиненных 
        let wrap = ''
        for (let m = 0; m < sub_ids.length; m++) {


            let report_event_container = '' // Контейнер Снижко Ю.И.

            if(reports_by_mid[sub_ids[m]]) {

                let week_reports = []
                for (let p = 0; p < reports_by_mid[sub_ids[m]].length; p++) {
 

                    //Cортировка по ключу JS6
                    /*
                                    if(    title_date[   reports_by_mid[   sub_ids[m] ][p]['week']    ] ){

                                    }

                    */
                    //Фильтрация по week
                    if(!week_reports[reports_by_mid[sub_ids[m]][p]['week']]) {
                        week_reports[reports_by_mid[sub_ids[m]][p]['week']] = []
                    }


                    week_reports[reports_by_mid[sub_ids[m]][p]['week']].push(reports_by_mid[sub_ids[m]][p])
                        //Бути обережным бо у нас ключи undefined! 


                }

                week_reports = week_reports.filter(function(e) {
                    return e != undefined;
                })


               // debugger
                let thead = '<div class="event-wrap clearfix"><table>'


                let html = '<div class="event-wrap-scroll">'
                for (let l = 0; l < week_reports.length; l++) {


                    let caption = (new Date(week_reports[l][0]['from_date'])).getDate() + ' - ' + (new Date(week_reports[l][0]['to_date'])).getDate() +
                    ' ' + getRussianMonth(new Date( week_reports[l][0]['to_date'] ).getMonth())


                    //html += '<table><caption>' + week_reports[l][0]['week'] + '</caption>'
                      html += '<table><caption>' + caption + '</caption><tr>'+
                            '<th>Д.Г.<br>к-во</th><th>Д.Г.<br>пож.</th><th>Ноч.<br>к-во</th>'+
                            '<th>Сл.<br>к-во</th><th>Сл.<br>нов.</th><th>Сл.<br>пок.</th>'+
                        '</tr>'

                     //html +='<tr></tr>' 
                    let report_parent_by_current_week = reports_by_mid[my_id].filter(function (el) {
                        return el.uid == sub_ids[m] && week_reports[l][0]['week'] == el.week
                     })

                     //week_reports[l].unshift(report_parent_by_current_week[0])


                      html+= 
                        '<tr>'+
                            '<td>'+ report_parent_by_current_week[0]['home_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['home_as_leader_value']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['night_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_coming_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_as_leader_repentance_count']  +'</td>'+
                        '</tr>'


                     //window.thead = ''
                    for (let s = 0; s < week_reports[l].length; s++) {




                        html += '<tr>'
                        for (let prop in week_reports[l][s]) {

                        if( prop == 'fullname'  && l == 0){
                            if(s ==0){

                                thead +=  '<caption>'+ report_parent_by_current_week[0]['fullname']   +'</caption>'+
                        '<tr>'+
                            '<th>Подчиненные</th>'+
                        '</tr>'+
                        '<tr><td>'+  report_parent_by_current_week[0]['fullname']  +'</td></tr>'
                               // console.log(  week_reports[l][s]['fullname']   )
                            }
                            thead += '<tr><td>'+  week_reports[l][s]['fullname']  +'</td></tr>'
                        }
                            //if(jQuery.inArray(prop, ['id', 'mid', 'uid', 'week', 'from_date', 'to_date']) != -1) continue
                            if(jQuery.inArray(prop, [ 'home_count', 'home_value', 'night_count', 'service_count', 'service_coming_count','service_repentance_count']) == -1) continue
                            html += '<td data-prop="' + prop + '">' + week_reports[l][s][prop] + '</td>'
                        }
                        html += '</tr>'


                       
                    }


                     //Сумма 
                        
                        html += '<tr class="marg">'+
                            '<td></td><td></td><td></td><td></td><td></td><td></td>'+
                        '</tr>'
                        html+= 
                        '<tr>'+
                            '<td>'+ report_parent_by_current_week[0]['home_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['home_value']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['night_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_coming_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_repentance_count']  +'</td>'+
                        '</tr>'
                       

                    html += '</table>'
                }
                 thead += '<tr class="marg">'+
                            '<td></td></tr><tr><td>Сумма:</td>'+
                        '</tr></table>'
                //console.log(thead)
                  html = thead + html;
                 //  console.log(html)


                html += '</div></div>'
                report_event_container += html
                wrap += report_event_container

            }
        }

        //console.log(  new Date().getTime() )
        document.getElementById(container).innerHTML = wrap

    if(callback){
        callback()
    }



    })
}






function getWeekShortReports(period,container,callback){
    ajaxRequest(CONFIG.DOCUMENT_ROOT + period, null, function(data) {


        let results = data.results;


        if( !results.length){
          //  showPopup('Не созданные репорты')
            return ''
        }

        window.reports_by_mid = [] //[2,120]



        //  reports_by_mid = [ 0: [{},{}]  ]
        for (let i = 0; i < results.length; i++) {
            let report = results[i];


            if(!reports_by_mid[report['mid']]) {
                reports_by_mid[report['mid']] = []
            }
            reports_by_mid[report['mid']].push(report)
        }


        //Берем id подчиненных на мені  

        window.sub_ids = []; //[3, 5, 6, 7, 8, 120]

        if(  !reports_by_mid[my_id] ){
           //  showPopup('Не созданные репорты')
            return ''
        }

        for (let j = 0; j < reports_by_mid[my_id].length; j++) {

            if( jQuery.inArray( reports_by_mid[my_id][j]['uid'], sub_ids ) == -1){
                 sub_ids.push(reports_by_mid[my_id][j]['uid'])
            } 
           
        }


        //Генерация отчетов по подчиненных 
        let wrap = ''
        window.week_reports = [];

        console.log(sub_ids)
        for (let m = 0; m < sub_ids.length; m++) {
          if(reports_by_mid[sub_ids[m]]) {

              let report_event_container = ''


              let report_parent_by_current_week = reports_by_mid[my_id].filter(function (el) {
                        return el.uid == sub_ids[m] //&& week_reports[l][0]['week'] == el.week
                     })


              for (let l = 0; l < report_parent_by_current_week.length; l++) {



              if(!week_reports[report_parent_by_current_week[l]['week']]) {
                        week_reports[report_parent_by_current_week[l]['week']] = []
                    }


               week_reports[report_parent_by_current_week[l]['week']].push(  report_parent_by_current_week[l]     )

          }


          
        }




            }
           
                week_reports = week_reports.filter(function(e) {
                    return e != undefined;
                });


/****/


               // debugger
        let thead = '<div class="event-wrap clearfix"><table>'


        let html = '<div class="event-wrap-scroll">'
        for (let l = 0; l < week_reports.length; l++) {


            let caption = (new Date(week_reports[l][0]['from_date'])).getDate() + ' - ' + (new Date(week_reports[l][0]['to_date'])).getDate() +
                    ' ' + getRussianMonth(new Date( week_reports[l][0]['to_date'] ).getMonth())


                    //html += '<table><caption>' + week_reports[l][0]['week'] + '</caption>'
                      html += '<table><caption>' + caption + '</caption><tr>'+
                            '<th>Д.Г.<br>к-во</th><th>Д.Г.<br>пож.</th><th>Ноч.<br>к-во</th>'+
                            '<th>Сл.<br>к-во</th><th>Сл.<br>нов.</th><th>Сл.<br>пок.</th>'+
                        '</tr>'



                     //week_reports[l].unshift(report_parent_by_current_week[0])




                     //window.thead = ''
            for (let s = 0; s < week_reports[l].length; s++) {




                        html += '<tr>'
                for (let prop in week_reports[l][s]) {

                        if( prop == 'fullname'  && l == 0){
                            if(s ==0){

                                thead +=  '<caption>&nbsp; </caption>'+
                        '<tr>'+
                            '<th>Подчиненные</th>'+
                        '</tr>'
                       
                               // console.log(  week_reports[l][s]['fullname']   )
                            }
                            thead += '<tr><td>'+  week_reports[l][s]['fullname']  +'</td></tr>'
                        }
                            //if(jQuery.inArray(prop, ['id', 'mid', 'uid', 'week', 'from_date', 'to_date']) != -1) continue
                           // if(jQuery.inArray(prop, [ 'home_count', 'home_value', 'night_count', 'service_count', 'service_coming_count','service_repentance_count']) == -1) continue
                            
                           if(jQuery.inArray(prop, [ 'home_as_leader_count', 'home_as_leader_value', 'night_as_leader_count', 'service_as_leader_count', 'service_as_leader_coming_count','service_as_leader_repentance_count']) !== -1) {
                            html += '<td data-prop="' + prop + '">' + week_reports[l][s][prop] + '</td>'
                           }
                            
                        }
                        html += '</tr>'


                       
                    }


                     //Сумма 
                        
                        html += '<tr class="marg">'+
                            '<td></td><td></td><td></td><td></td><td></td><td></td>'+
                        '</tr>'

                       
                      // debugger

            let report_parent_by_current_week = reports_by_mid[my_id].filter(function (el) {

                            //return el.uid == sub_ids[m]
                         // debugger

                        return /*el.uid == my_id &&*/ week_reports[l][0]['week'] == el.week
                     })
                        console.log(report_parent_by_current_week)
/*
                        html+= 
                         '<tr>'+
                            '<td>'+ report_parent_by_current_week[0]['home_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['home_value']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['night_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_coming_count']  +'</td>'+
                           '<td>'+ report_parent_by_current_week[0]['service_repentance_count']  +'</td>'+
                        '</tr>'
                    */  

                    html += '</table>'
                }
                 thead += '<tr class="marg">'+
                            '<td></td></tr>'+
                        '</table>'
                //console.log(thead)
                  html = thead + html;
                 //  console.log(html)


                html += '</div></div>'
                report_event_container += html
                wrap += report_event_container



/**************/
document.getElementById(container).innerHTML = wrap



    if(callback){
        callback()
    }



    })
}
