import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


def youtube_video_validator(value):
    pattern = r'^(https://youtube.com/embed/|https://www.youtube.com/embed/|https://youtu.be/)' + \
              r'[-_\da-zA-Z]+(\?(\w*=\w*)?)?(&(\w+=\w*)?)*$'
    if re.match(pattern, value) is not None:
        return
    raise ValidationError(_('Введите ссылку на youtube.com видео.'))


class YoutubeURLField(models.URLField):
    default_validators = [validators.URLValidator(), youtube_video_validator]

    def _parse_params(self, parameters):
        params = list()
        seconds = 0
        for k, v in [p.split('=', 1) for p in parameters.split('&')]:
            if k != 't':
                params.append(f'{k}={v}')
                continue
            for t in re.findall(r'\d+[smh]', v):
                digit, unit = t[:-1], t[-1]
                if unit == 's':
                    seconds += int(digit)
                elif unit == 'm':
                    seconds += int(digit) * 60
                elif unit == 'h':
                    seconds += int(digit) * 3600
            params.append(f'start={seconds}')
        return '&'.join(params)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        value = value.split("/")[-1]
        if '?' in value:
            value, parameters = value.split("?", 1)
            value = '?'.join([value, self._parse_params(parameters)])
        return 'https://www.youtube.com/embed/{value}'.format(value=value)
