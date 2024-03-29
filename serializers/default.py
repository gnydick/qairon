from flask_restless.serialization import DefaultSerializer

from qairon_qcli.controllers.output_controller import AbstractOutputController, simplify_row


class QcliSerializer(DefaultSerializer):
    """Default Serializer implementation."""

    def __init__(self, model, type_name, api_manager, primary_key=None, only=None, exclude=None,
                 additional_attributes=None, **kwargs):
        super().__init__(model, type_name, api_manager, primary_key, only, exclude, additional_attributes, **kwargs)

    def serialize(self, instance, only=None):
        oc = AbstractOutputController()
        data = super().serialize(instance, only)
        return simplify_row(data)
