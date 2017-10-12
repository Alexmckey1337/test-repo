'use strict';
import URLS from '../Urls/index';
import {showStatPopup} from "../Popup/popup";
import {showAlert} from "../ShowNotifications/index";

export default class PrintMasterStat {
    constructor(summitId) {
        this.summit = summitId;
        this.masterId = null;
        this.filter = [];
        this.url = URLS.summit.master(summitId)
    }

    setMaster(id) {
        this.masterId = id;
    }

    setFilterData(data) {
        this.setMaster(data.id);
        if (data.attended) {
            this.filter.push({
                attended: data.attended,
            });
        }
        if (data.date) {
            this.filter.push({
                date: data.date
            });
        }
        this.makeLink();
    }

    getMasters() {
        let defaultOption = {
            method: 'GET',
            credentials: "same-origin",
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
        return fetch(URLS.summit.bishop_high_masters(this.summit), defaultOption)
            .then(res => res.json());
    }

    show() {
        this.getMasters()
            .then(data => data.map(item => `<option value="${item.id}">${item.full_name}</option>`))
            .then(options => {
                let content = `
                    <div class="block">
                        <ul class="info">
                            <li>
                                <div class="label-wrapp">
                                    <label>Выберите ответсвенного</label>
                                </div>
                                <div class="input">
                                    <select class="master">`; content += options.join(','); content += `</select>
                                </div>
                            </li>
                            <li>
                                <div class="label-wrapp">
                                    <label>Пристутствие</label>
                                </div>
                                <div class="input">
                                    <select class="attended">
                                        <option value="">ВСЕ</option>
                                        <option value="true">ДА</option>
                                        <option value="false">НЕТ</option>
                                    </select>
                                </div>
                            </li>
                            <li>
                                <div class="label-wrapp">
                                    <label>Дата</label>
                                </div>
                                <div class="input">
                                    <input class="date" type="text">
                                </div>
                            </li>
                        </ul>
                    </div>`;
                showStatPopup(content, 'Сформировать файл статистики', this.setFilterData.bind(this));
            });

    }

    print() {
        if (!this.masterId) {
            showAlert('Выберите мастера для печати');
            return
        }
        let defaultOption = {
            method: 'GET',
            credentials: "same-origin",
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
        return fetch(`${this.url}${this.masterId}.pdf`, defaultOption).then(data => data.json()).catch(err => err);
    }

    makeLink() {
        console.log(this.filter);
        if (!this.masterId) {
            showAlert('Выберите мастера для печати');
            return
        }
        let link = `${this.url}${this.masterId}.pdf?`;
        this.filter.forEach(item => {
            let key = Object.keys(item);
            link += `${key[0]}=${item[key[0]]}&`
        });
        link += 'short';
        showAlert(`<a class="btn" href="${link}">Скачать</a>`, 'Скачать статистику');
    }
}