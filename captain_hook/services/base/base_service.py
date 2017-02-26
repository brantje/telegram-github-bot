from __future__ import absolute_import
import importlib
from utils import strings


class BaseService:

    def __init__(self, request, body, comms, config):
        self.request = request
        self.body = body
        self.comms = comms
        self.config = config

    def execute(self):
        message_dict = self._get_event_processor(self.event).process()
        for name, comm in self.comms.items():
            default_message = message_dict.get('default', None)
            comm.communicate(message_dict.get(name, default_message))
        return "ok"

    def _get_event_processor(self, event):
        try:
            event_module = self._import_event_module(event)
        except ImportError:
            print("Doesn't know how to handle {}".format(event))

        event_processor_class_name = "{}Event".format(
            strings.toCamelCase(event),
        )
        return getattr(event_module, event_processor_class_name)(
            request=self.request,
            body=self.body,
            config=self.config,
            event=event
        )

    def _import_event_module(self, event):
        package = "services.{}.events".format(
            strings.toSnakeCase(
                self.__class__.__name__.split('Service')[0]
            )
        )
        importlib.import_module(package)

        return importlib.import_module(
            ".{}".format(event),
            package=package
        )