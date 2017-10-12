'use strict';

export default class DeleteUser {
    constructor(id, userName, title) {
        this.user = id;
        this.user_name = userName;
        this.title = title;
    }

    deleteUser() {
        return this.user
    }

    btn() {
        let btn = document.createElement('button');
        return $(btn).on('click', this.deleteUser.bind(this));
    }

    popup(massage = null, info = null) {
        if (massage) {
            console.log(massage)
        }
        let btn = this.btn();
        let popup = document.getElementById('create_pop');
        let container = document.createElement('div');
        if (popup) {
            popup.parentElement.removeChild(popup)
        }

        let body = `<div class="pop_cont pop-up__confirm" >
            <div class="top-text">
                <h3>Удаление пользователя</h3><span class="close_pop">×</span>
            </div>
                <div class="main-text">
                    <p>${(massage) ? massage : `Вы действительно хотите удалить пользователя ${this.user_name} из ${this.title}?` }</p>
                    ${(info) ? info : ''}
                    <div class="buttons"></div>
                </div>
            </div>`;

        container.className = "pop-up-universal";
        container.innerHTML = body;

        $(container).find('.buttons').html(btn);
        container.id = "create_pop";
        $(container).find('.close_pop').on('click', function () {
            $('.pop-up-universal').css('display', 'none').remove();
        });

        $('body').append(container);
    }
}