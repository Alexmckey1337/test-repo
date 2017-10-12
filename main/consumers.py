from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer
from channels.handler import AsgiHandler
from channels.sessions import channel_session
from django.http import HttpResponse


@channel_session
def ws_connect(message, room):
    message.reply_channel.send({"accept": True})
    message.channel_session['room'] = room
    Group("chat-%s" % room).add(message.reply_channel)


@channel_session
def ws_echo(message):
    Group("chat-%s" % message.channel_session['room']).send({
        "text": message['text'],
    })


@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['room']).discard(message.reply_channel)


def poll_consumer(message):
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


class UserConsumer(JsonWebsocketConsumer):
    http_user = True

    def connection_groups(self, **kwargs):
        user = kwargs.get('user')
        return [
            'payments_%s' % user,
            'disciples_%s' % user,
            'summit_%s_ticket' % user,
            'summit_email_code_error_%s' % user,
            'export_%s' % user,
        ]
