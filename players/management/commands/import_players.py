import re
from django.core.management.base import BaseCommand
from players.models import Player

class Command(BaseCommand):
    help = 'Import initial players from the provided list'

    def handle(self, *args, **kwargs):
        players_data = """
Aashit Srivastava	9690009945
Abhay Shukla	8181828027
Abhay Singh	7905168891
Abhishek Pandey	7897235775
Abhishek Rai	8299857692
Ajeet Verma	9918771755
Akash Pandey	9044287798
Akhil Singh	9260921900
Amit Singh (Bade)	9936649911
Amit Singh (Chhotu)	8604789100
Amit Singh- Bhaiya	9415180824
Apporv Patel	8423067262
Ayush Mishra	8840748349
Deepak Kanaujiya	9044824759
Deepak Sahni	7985236752
Dr Atul Yadav	8738060535
Dr Kalim	9140019698
Gaurav Tripathi	6388851372
Hassan	8800342162
Imran
Karan Singh	7398855007
Kaushal Katiyar	9919192260
Madhusoodan Shukla	9335154865
Mahendra Yadav	7905623794
Rahul Verma	9454321925
Ramiz (Sekhu)	9999815448
Rishab Dubey	6394548224
Saud	9369990152
Saurabh Yadav	9899664919
Shalu	7007634961
Shivakant Mishra	7275050518
Shivam Singh	8400302089
Shubham Singh	9450944877
Sunil Kumar	8765180051
Vivek Pandey	9076949416
Zikrul	7065196383
"""

        lines = players_data.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to extract name and phone number
            # Regex to find name followed by optional whitespace and phone number (digits)
            # Or just name if no phone

            # Since some lines might have tabs or spaces, we split carefully
            # The pattern is Name (which may contain spaces) followed by Phone (digits) at the end

            match = re.search(r'^(.*?)\s+(\d+)$', line)

            if match:
                name_part = match.group(1).strip()
                phone_number = match.group(2).strip()
            else:
                # No phone number found (e.g. "Imran")
                name_part = line.strip()
                phone_number = None

            # Split name into first and last
            parts = name_part.split(' ', 1)
            if len(parts) > 1:
                first_name = parts[0]
                last_name = parts[1]
            else:
                first_name = parts[0]
                last_name = ""

            # Check if player exists by phone number
            if phone_number:
                if Player.objects.filter(phone_number=phone_number).exists():
                    self.stdout.write(self.style.WARNING(f'Player with phone {phone_number} already exists: {first_name} {last_name}'))
                    continue
            else:
                # Check if player exists by name (only if phone is None, e.g. Imran)
                if Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                    self.stdout.write(self.style.WARNING(f'Player already exists: {first_name} {last_name}'))
                    continue

            # Create the player
            try:
                player = Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    age=0,  # Default
                    role='all_rounder'  # Default
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created player: {first_name} {last_name} ({phone_number})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating player {first_name} {last_name}: {str(e)}'))
