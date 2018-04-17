import json

from django.conf import settings
from django.http import QueryDict
from django.http.multipartparser import MultiPartParserError, MultiPartParser as DjangoMultiPartParser
from django.utils import six
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser, DataAndFiles


class MultiPartAndJsonParser(BaseParser):
    """
    Parser for multipart form data, which may include file data.
    Some fields can be parsed as json.
    """
    media_type = 'multipart/form-data'

    @staticmethod
    def _parse_json(data, name):
        """
        QueryDict[name] = "['first',2]" => return list == ["first", 2]
        QueryDict[name] = "{'nome':'value','a':2}" => return dict == {"name": "value", "a": 2}

        :param data: QueryDict
        :param name: str
        :return: list or dict (or other valid json value)
        :return: None if json is invalid
        """
        field_value = data.get(name, '')
        try:
            field_value = json.loads(field_value)
        except ValueError:
            return None
        return field_value

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a multipart encoded form,
        and returns a DataAndFiles object.

        `.data` will be a `QueryDict` containing all the form parameters.
        `.files` will be a `QueryDict` containing all the form files.

        `list_fields` and `dict_fields` parsed as json.

        For example:
        class BookViewSet(viewsets.ModelViewSet):
            ...
            parser_list_fields = ['tags', 'authors']
            parser_dict_fields = ['some_data']
            parser_classes = (MultiPartAndJsonParser,)

        ------------------------------------------------------------
        multipart/form-data; boundary=42940404204

            --42940404204
            Content-Disposition: form-data; name="tags"

            ["python","django","parsers"]
            --42940404204
            Content-Disposition: form-data; name="authors"

            ["Bill","Linus"]
            --42940404204
            Content-Disposition: form-data; name="some_data"

            {"a":"b","c":"d","e":["f","g"]}
            --42940404204--
        ------------------------------------------------------------

        request.data == {
            ...
            "tags": ["python", "django", "parsers"],
            "authors": ["Bill", "Linus"]
            "some_data": {
                "a": "b",
                "c": "d",
                "e": ["f", "g"]
            }
            ...
        }

        """
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        meta = request.META.copy()
        meta['CONTENT_TYPE'] = media_type
        upload_handlers = request.upload_handlers

        list_fields = getattr(parser_context['view'], 'parser_list_fields', [])
        dict_fields = getattr(parser_context['view'], 'parser_dict_fields', [])

        try:
            parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            if isinstance(data, QueryDict):
                data._mutable = True

            for field_name in list_fields:
                field_value = self._parse_json(data, field_name)
                if field_value is not None:
                    data.setlist(field_name, field_value)

            for field_name in dict_fields:
                field_value = self._parse_json(data, field_name)
                if field_value is not None:
                    data[field_name] = field_value
            if isinstance(data, QueryDict):
                data._mutable = False

            return DataAndFiles(data, files)
        except MultiPartParserError as exc:
            raise ParseError('Multipart form parse error - %s' % six.text_type(exc))
