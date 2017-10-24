'use strict';
import URLS from '../Urls/index';
import DeleteUser from './deleteUser';

export default class DeleteHomeGroupUser extends DeleteUser {
    constructor(groupId, userId, callback, userName, title) {
        super(userId, userName, title);
        this.home_group = groupId;
        this.callback = callback;
        this.show_delete = true;
    }

    btn() {
        if (!this.show_delete) {
            return
        }
        let container = document.createElement('div');
        let btn = document.createElement('button');
        let cancel = document.createElement('button');
        $(container).addClass('btn_block');
        $(btn).text('Подтвердить').addClass('ok').on('click', this.deleteFromHomeGroup.bind(this));
        $(cancel).text('Отменить').addClass('close_pop');
        $(container).append(cancel).append(btn);
        return container
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
        return fetch(URLS.home_group.del_user(this.home_group), options)
            .then(res => {
                return (res.status == 204) ? res.status : res.json()
            })
            .then(data => {
                if (data === 204) {
                    this.show_delete = false;
                    this.popup('Пользователь удален из домашней группы');
                    this.callback();
                }
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }
}