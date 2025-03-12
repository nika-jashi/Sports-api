from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.tournaments.models import Tournament, Team, TeamMember


class TournamentSerializer(serializers.ModelSerializer):
    """ Tournament Serializer """

    class Meta:
        model = Tournament
        fields = ['slug', 'name', 'description', 'format', 'tournament_image', 'start_date', 'end_date', 'team_size',
                  'number_of_participants', 'creator', 'created_at', 'is_active']
        read_only_fields = ['creator', 'created_at', 'is_active', 'slug']

    def validate(self, data):
        if data.get('format') == 'single_elimination' or data.get('format') == 'double_elimination':
            number_of_participants = data.get('number_of_participants')
            if number_of_participants < 2 or (number_of_participants & (number_of_participants - 1)) != 0:
                raise serializers.ValidationError(
                    {"number_of_participants": _(
                        "Number of participants must be a power of 2 (e.g., 2, 4, 8, 16, etc.)")
                    }
                )
        return data

    def create(self, validated_data):
        """ Create And Return A Tournament With Filled Information """
        instance = Tournament.objects.create(**validated_data, is_active=True)
        return instance


class TeamSerializer(serializers.ModelSerializer):
    """ Team Serializer """

    class Meta:
        model = Team
        fields = ['name', 'tournament', 'leader', 'is_active']
        read_only_fields = ['tournament', 'leader', 'is_active']

    def create(self, validated_data):
        """ Create And Return A Team With Filled Leader Information """
        instance = Team.objects.create(**validated_data, is_active=True)
        return instance


class TeamMemberSerializer(serializers.ModelSerializer):
    """ Team Members Serializer """

    class Meta:
        model = TeamMember
        fields = ['member', 'team']
        read_only_fields = ['member', 'team']

    def create(self, validated_data):
        """ Create And Return A Team Member With Filled Information """
        instance = TeamMember.objects.create(**validated_data)
        return instance
