from django.shortcuts import render

# Create your views here.
# music/views.py
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Song, Artist, Comment

def song_list(request):
    """歌曲列表页（主页）"""
    songs = Song.objects.all().order_by('title')
    paginator = Paginator(songs, 20)  # 每页20首歌
    
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except:
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'current_page': page_number,
        'page_title': '歌曲列表'
    }
    return render(request, 'music/song_list.html', context)

def song_detail(request, song_id):
    """歌曲详情页"""
    song = get_object_or_404(Song, id=song_id)
    comments = Comment.objects.filter(song=song).order_by('-created_at')
    
    context = {
        'song': song,
        'comments': comments,
        'page_title': song.title
    }
    return render(request, 'music/song_detail.html', context)

def artist_list(request):
    """歌手列表页"""
    artists = Artist.objects.all().order_by('name')
    paginator = Paginator(artists, 20)  # 每页20位歌手
    
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except:
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'current_page': page_number,
        'page_title': '歌手列表'
    }
    return render(request, 'music/artist_list.html', context)

def artist_detail(request, artist_id):
    """歌手详情页"""
    artist = get_object_or_404(Artist, id=artist_id)
    songs = Song.objects.filter(artist=artist.name).order_by('title')
    
    context = {
        'artist': artist,
        'songs': songs,
        'page_title': artist.name
    }
    return render(request, 'music/artist_detail.html', context)

def search(request):
    """搜索页"""
    return render(request, 'music/search.html', {'page_title': '搜索'})

def search_results(request):
    """搜索结果页"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'song')
    
    if not query:
        return redirect('search')
    
    start_time = time.time()
    results = []
    total_count = 0
    
    if search_type == 'song':
        # 搜索歌曲：歌曲名、歌手名、歌词
        songs = Song.objects.filter(
            Q(title__icontains=query) |
            Q(artist__icontains=query) |
            Q(lyric__icontains=query)
        ).distinct()
        results = songs
        total_count = songs.count()
    else:  # search_type == 'artist'
        # 搜索歌手：歌手名、简介
        artists = Artist.objects.filter(
            Q(name__icontains=query) |
            Q(abstract__icontains=query)
        ).distinct()
        results = artists
        total_count = artists.count()
    
    search_time = time.time() - start_time
    
    # 分页
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'search_type': search_type,
        'total_count': total_count,
        'search_time': round(search_time, 3),
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'page_title': f'搜索结果: {query}'
    }
    return render(request, 'music/search_results.html', context)

@require_POST
@csrf_exempt
def add_comment(request, song_id):
    """添加评论"""
    song = get_object_or_404(Song, id=song_id)
    content = request.POST.get('content', '').strip()
    
    if content:
        comment = Comment.objects.create(
            song=song,
            content=content
        )
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return JsonResponse({'success': False, 'error': '评论内容不能为空'})

@require_POST
@csrf_exempt
def delete_comment(request, comment_id):
    """删除评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return JsonResponse({'success': True})
