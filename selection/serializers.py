from rest_framework import serializers
from .models import  SelectionState, BecaTrabajo

class SelectionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionState
        fields = "__all__"

class AssignationSerializer(serializers.Serializer):
    beca = serializers.SerializerMethodField()

    def get_beca(self, obj):
        fullname = ' '.join( 
            map (
                lambda x: x.capitalize(), 
                f'{obj['beca__first_name']} {obj['beca__last_name']}'.split(' ')
            )  
        )
        beca_data = {
            'code': obj['beca__code'],
            'full_name': fullname,
            'email': obj['beca__email'],
            'photo': obj['beca__photo'],
            'address': obj['beca__address'],
            'gender': obj['beca__gender'],
            'career': obj['beca__career'],
            'extra_studies': obj['beca__extra_studies'],
            'motivation': obj['beca__motivation'],
            'status': obj['status'],
            'percentage': obj['percentage'],
            'notified': obj['notified'],
            'ubication': {
                'id': obj['schedule__ubication__id'],
                'name': obj['schedule__ubication__name'],
            }
        }
        return beca_data
class BecaTrabajoListForm(serializers.ModelSerializer):

    class Meta:
        model = BecaTrabajo
        fields = ['first_name', 'last_name', 'email', 'photo', 'sended_form']