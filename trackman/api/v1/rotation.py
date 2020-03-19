from flasgger import swag_from
from trackman import models, ma
from .base import TrackmanResource


class RotationListSchema(ma.Schema):
    rotations = ma.Dict(keys=ma.Integer(), values=ma.String())


class RotationList(TrackmanResource):
    @swag_from({
        'operationId': "getRotations",
        'tags': ['private'],
        'responses': {
            200: {
                'schema': RotationListSchema,
            },
        },
    })
    def get(self):
        """Get a dictionary of rotations where the rotation ID is the key and
        the rotation name is the value."""
        rotations = {}
        for i in models.Rotation.query.filter_by(visible=True).order_by(
                models.Rotation.id).all():
            rotations[i.id] = i.rotation

        rotation_list_schema = RotationListSchema()
        return rotation_list_schema.dump({'rotations': rotations})
