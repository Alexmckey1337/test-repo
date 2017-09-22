'use strict';
import URLS from '../Urls/index';
import DeleteUser from './deleteUser';

export default class DeleteChurchUser extends DeleteUser {
    constructor(userId, churchId, callback, userName, title) {
        super(userId, userName, title);
        this.church = churchId;
        this.callback = callback;
        this.delAll = false;
        this.show_delete = true;
        this.home_group = [];
    }

    btn() {
        if (!this.show_delete) {
            return
        }
        let container = document.createElement('div');
        let btn = document.createElement('button');
        let cancel = document.createElement('button');
        $(container).addClass('btn_block');
        (this.delAll) ?
            $(btn).text('Удалить из домашних групп').addClass('ok').on('click', this.deleteFromHomeGroup.bind(this)) :
            $(btn).text('Подтвердить').addClass('ok').on('click', this.deleteFromChurch.bind(this));
        $(cancel).text('Отменить').addClass('close_pop');
        $(container).append(cancel).append(btn);
        return container
    }

    deleteFromChurch() {
        let options = {
            method: 'POST',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                user_id: this.user
            })
        };
        return fetch(URLS.church.del_user(this.church), options)
            .then(res => {
                return (res.status == 204) ? res.status : res.json()
            })
            .then(data => {
                if (data !== 204 && data.home_groups) {
                    let info = data.home_groups.map(item => `<p>Состоит в ${item.name}</p>`);
                    this.home_group = data.home_groups.map(item => item.id);
                    this.delAll = true;
                    this.popup(data.detail, info)
                }
                if (data === 204) {
                    this.show_delete = false;
                    this.popup('Пользователь удален из церкви');
                    this.callback();
                }
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }

    deleteFromHomeGroup() {
        let options = {
            method: 'POST',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                user_id: this.user
            })
        };
        this.delAll = false;
        let massage = 'Пользователь удален из домашней группы';
        let info = '<p>Подтвердите удаление пользователя из церкви</p>';
        Promise.all(this.home_group.map((item) => {
            fetch(URLS.home_group.del_user(item), options)
        }))
            .then(() => {
                this.home_group = [];
                this.popup(massage, info);
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }
}