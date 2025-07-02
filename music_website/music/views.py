from django.shortcuts import render

# Create your views here.
# music/views.py
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Song, Singer, Comment


def song_list(request):
    """歌曲列表页（主页）"""
    songs = Song.objects.select_related('singer').all()
    paginator = Paginator(songs, 20)  # 每页歌曲数量：20
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }
    return render(request, 'music/song_list.html', context)


def song_detail(request, song_id):
    """歌曲详情页"""
    song = get_object_or_404(Song, id=song_id)
    comments = song.comments.all()
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(song=song, content=content)
            return redirect('song_detail', song_id=song_id)
    
    context = {
        'song': song,
        'comments': comments,
    }
    return render(request, 'music/song_detail.html', context)


def singer_list(request):
    """歌手列表页"""
    singers = Singer.objects.all()
    paginator = Paginator(singers, 20)  # 每页20位歌手
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }
    return render(request, 'music/singer_list.html', context)

def singer_detail(request, singer_id):
    """歌手详情页"""
    singer = get_object_or_404(Singer, id=singer_id)
    songs = singer.songs.all()
    
    context = {
        'singer': singer,
        'songs': songs,
    }
    return render(request, 'music/singer_detail.html', context)

def search(request):
    """搜索页"""
    return render(request, 'music/search.html')

def search_results(request):
    """搜索结果页"""
    start_time = time.time()
    
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'song')  # song 或 singer
    page_number = request.GET.get('page', 1)
    
    results = []
    total_count = 0
    
    if query:
        if search_type == 'song':
            # 搜索歌曲：在歌曲名、歌手名、歌词中搜索
            songs = Song.objects.select_related('singer').filter(
                Q(title__icontains=query) |
                Q(singer__name__icontains=query) |
                Q(lyrics__icontains=query)
            ).distinct()
            total_count = songs.count()
            
            paginator = Paginator(songs, 20)
            page_obj = paginator.get_page(page_number)
            results = page_obj
            
        else:  # search_type == 'singer'
            # 搜索歌手：在歌手名、简介中搜索
            singers = Singer.objects.filter(
                Q(name__icontains=query) |
                Q(biography__icontains=query)
            )
            total_count = singers.count()
            
            paginator = Paginator(singers, 20)
            page_obj = paginator.get_page(page_number)
            results = page_obj
    
    search_time = round((time.time() - start_time) * 1000, 2)  # 转换为毫秒
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'total_count': total_count,
        'search_time': search_time,
        'page_obj': results if query else None,
    }
    return render(request, 'music/search_results.html', context)

@csrf_exempt
def delete_comment(request, comment_id):
    """删除评论"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        song_id = comment.song.id
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})