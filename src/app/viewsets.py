from typing import Any, Dict, Optional, Protocol, Type

from django.core.exceptions import ImproperlyConfigured
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet as _ReadOnlyModelViewSet

from app.validators import Validator

__all__ = [
    'AppViewSet',
    'ReadOnlyAppViewSet',
]


class ViewsetWithValidationProtocol(Protocol):
    validator_class: Optional[Type[Validator]]


class ValidationMixin(ViewsetWithValidationProtocol):
    def get_validator_class(self) -> Type[Validator]:
        if self.validator_class is None:
            raise ImproperlyConfigured('Please set validator_class class variable')

        return self.validator_class

    def _validate(self, data, context: Optional[dict] = None):
        Validator = self.get_validator_class()
        Validator.do(data, context=self.get_validator_context())

    def get_validator_context(self) -> Dict[str, Any]:
        return {
            'request': self.request,  # type: ignore
        }


class MultiSerializerMixin:
    def get_serializer_class(self, action=None):
        """
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = MyDefaultSerializer
            serializer_action_classes = {
               'list': MyListSerializer,
               'my_action': MyActionSerializer,
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.

        Thanks gonz: http://stackoverflow.com/a/22922156/11440

        """
        if action is None:
            action = self.action

        try:
            return self.serializer_action_classes[action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class ReadOnlyAppViewSet(MultiSerializerMixin, _ReadOnlyModelViewSet):
    pass


class AppViewSet(MultiSerializerMixin, ModelViewSet):
    def update(self, request, *args, **kwargs):
        """
        Always serialize response with the default serializer.

        CAUTION: we are loosing serializer context here!

        If you need it, feel free to rewrite this method with http://www.cdrf.co/3.6/rest_framework.mixins/UpdateModelMixin.html
        """
        response = super().update(request, *args, **kwargs)

        Serializer = self.get_serializer_class(action='retrieve')
        response.data = Serializer(self.get_object()).data

        return response

    def create(self, request, *args, **kwargs):
        """
        Always serialize response with the default serializer.

        CAUTION: we are loosing serializer context here!

        If you need it, feel free to rewrite this method with http://www.cdrf.co/3.6/rest_framework.mixins/CreateModelMixin.html
        """
        response = super().create(request, *args, **kwargs)

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            self.kwargs[lookup_url_kwarg] = response.data.get(self.lookup_field) or response.data['id']
        except KeyError:
            return response  # if you want to mangle with response serializing, please provide ID or lookup_url_kwarg in your serializer

        Serializer = self.get_serializer_class(action='retrieve')
        response.data = Serializer(self.get_object()).data

        return response
