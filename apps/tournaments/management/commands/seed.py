from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.users.models import CustomUser, CustomUserProfile
from apps.tournaments.models import Tournament, Team, TeamMember


class Command(BaseCommand):
    help = 'Seed the database with 4 users and 2 tournaments (not started yet)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding initial data..."))

        # 1. Create 4 users
        users_data = [
            {'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Smith'},
            {'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
            {'email': 'carol@example.com', 'first_name': 'Carol', 'last_name': 'Williams'},
            {'email': 'dave@example.com', 'first_name': 'Dave', 'last_name': 'Brown'},
            {'email': 'john@example.com', 'first_name': 'john', 'last_name': 'doe'},
            {'email': 'ana@example.com', 'first_name': 'ana', 'last_name': 'khvedelidze'},
            {'email': 'ozzy@example.com', 'first_name': 'ozzy', 'last_name': 'osbourne'},
            {'email': 'kaxa@example.com', 'first_name': 'kaxa', 'last_name': 'meladze'},
        ]
        users = []

        for data in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('Password123!')
                user.save()
                self.stdout.write(f"Created user: {user.email}")
            else:
                self.stdout.write(f"User already exists: {user.email}")

            CustomUserProfile.objects.get_or_create(user=user)
            users.append(user)

        # 2. Create 2 upcoming tournaments
        today = date.today()
        tournament_data = [
            {
                'name': 'Summer Championship',
                'format': 'single_elimination',
                'team_size': '1',
                'start_date': today + timedelta(days=5),
                'end_date': today + timedelta(days=10),
                'creator': users[0]
            },
            {
                'name': 'Autumn Arena',
                'format': 'league',
                'team_size': '1',
                'start_date': today + timedelta(days=15),
                'end_date': today + timedelta(days=25),
                'creator': users[1]
            }
        ]

        tournaments = []
        for data in tournament_data:
            tournament, created = Tournament.objects.get_or_create(
                name=data['name'],
                defaults={
                    'format': data['format'],
                    'team_size': data['team_size'],
                    'start_date': data['start_date'],
                    'end_date': data['end_date'],
                    'creator': data['creator'],
                    'number_of_participants': 4,
                    'is_active': True,
                    'description': f"{data['name']} Description"
                }
            )
            if created:
                self.stdout.write(f"Created tournament: {tournament.name}")
            else:
                self.stdout.write(f"Tournament already exists: {tournament.name}")
            tournaments.append(tournament)

        # 3. Create Teams (one for each user per tournament)
        for tournament in tournaments:
            for user in users:
                team_name = f"{user.first_name}'s Team"
                team, created = Team.objects.get_or_create(
                    tournament=tournament,
                    leader=user,
                    defaults={'name': team_name, 'is_active': True}
                )
                TeamMember.objects.get_or_create(team=team, member=user)
                self.stdout.write(f"Assigned {user.email} to {tournament.name}")

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed."))
