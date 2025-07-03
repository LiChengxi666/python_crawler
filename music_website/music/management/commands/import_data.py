import csv
import os
from django.core.management.base import BaseCommand
from music.models import Artist, Song

class Command(BaseCommand):
    help = 'Import data from CSV files'
    
    def handle(self, *args, **options):
        # 导入歌手数据, 使用id做唯一标识
        artist_csv_path = '/home/python_crawler/data/artist_information.csv'
        if os.path.exists(artist_csv_path):
            with open(artist_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                artists_created = 0
                for row in reader:
                    artist, created = Artist.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'image_url': row.get('image_url', ''),
                            'abstract': row.get('abstract', ''),
                            'url': row.get('url', ''),
                            'cat': row.get('cat', ''),
                        }
                    )
                    if created:
                        artists_created += 1
                        self.stdout.write(f'Created artist: {artist.name}, totally: {artists_created}')
                self.stdout.write(f'Successfully imported {artists_created} artists')
        
        # 导入歌曲数据，使用id做唯一标识
        song_csv_path = '/home/python_crawler/data/song_information.csv'
        if os.path.exists(song_csv_path):
            with open(song_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                songs_created = 0
                for row in reader:
                    song, created = Song.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'artist': row['artist'],
                            'title': row['title'],
                            'album': row.get('album', ''),
                            'description': row.get('description', ''),
                            'image_url': row.get('image_url', ''),
                            'lyric': row.get('lyric', ''),
                            'time_points': row.get('time_points', ''),
                            'url': row.get('url', ''),
                            'lyric_url': row.get('lyric_url', ''),
                        }
                    )
                    if created:
                        songs_created += 1
                        self.stdout.write(f'Created song: {song.title}, totally: {songs_created}')
                self.stdout.write(f'Successfully imported {songs_created} songs')