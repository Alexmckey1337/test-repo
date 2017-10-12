'use strict';
import URLS from '../Urls/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index";
import getData from "../Ajax/index";

export function homeStatistics() {
    let data = {};
    Object.assign(data, getFilterParam());
    Object.assign(data, getTabsFilterParam());
    getData(URLS.event.home_meeting.stats(), data).then(data => {
        let tmpl = document.getElementById('statisticsTmp').innerHTML;
        let rendered = _.template(tmpl)(data);
        document.getElementById('statisticsContainer').innerHTML = rendered;
         $('.preloader').css('display', 'none');
    })
}