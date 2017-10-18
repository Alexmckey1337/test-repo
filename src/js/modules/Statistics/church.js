'use strict';
import URLS from '../Urls/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index";
import getData from "../Ajax/index";
import updateHistoryUrl from '../History/index';

export function churchStatistics() {
    let data = {};
    Object.assign(data, getFilterParam());
    Object.assign(data, getTabsFilterParam());
    updateHistoryUrl(data);
    getData(URLS.event.church_report.stats(), data).then(data => {
        let tmpl = document.getElementById('statisticsTmp').innerHTML;
        let rendered = _.template(tmpl)(data);
        document.getElementById('statisticsContainer').innerHTML = rendered;
        $('.preloader').css('display', 'none');
    })
}