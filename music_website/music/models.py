from django.db import models

# Create your models here.
from django.utils import timezone


global image_dir
image_dir = '/home/python_crawler/data/'


# Artist
class Artist(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    image_url = models.URLField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    cat = models.CharField(max_length=100, blank=True, null=True)
    songs = models.ManyToManyField('Song', related_name='artists')

    def __str__(self):
        return self.name
    
    def get_image_path(self):
        image_name = f'artist_image/{self.id}'
        return image_dir + image_name


# Song 与artist多对对关联
class Song(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    artist = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    lyric = models.TextField(blank=True, null=True)
    time_points = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    lyric_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def get_image_path(self):
        image_name = f'song_image/{self.id}'
        return image_dir + image_name
    
    def get_artist_obj(self):
        try:
            return Artist.objects.filter(name=self.artist).first()
        except:
            return None


# comment
class Comment(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on {self.song.title}: {self.content[:50]}"