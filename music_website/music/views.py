from django.shortcuts import render

# Create your views here.
# music/views.py
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from .models import Song, Artist, Comment
from django.contrib import messages


def song_list(request):
    """歌曲列表页（主页）"""
    songs = Song.objects.all().order_by("title")
    paginator = Paginator(songs, 50)  # 每页20首歌

    page_number = request.GET.get("page", 1)
    try:
        page_number = int(page_number)
    except:
        page_number = 1

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_pages": paginator.num_pages,
        "current_page": page_number,
        "page_title": "歌曲列表",
    }
    return render(request, "music/song_list.html", context)


def song_detail(request, song_id):
    """歌曲详情页"""
    song = get_object_or_404(Song, id=song_id)
    comments = Comment.objects.filter(song=song).order_by("-created_at")

    context = {"song": song, "comments": comments, "page_title": song.title}
    return render(request, "music/song_detail.html", context)


def artist_list(request):
    """歌手列表页"""
    artists = Artist.objects.all().order_by("name")
    paginator = Paginator(artists, 20)  # 每页20位歌手

    page_number = request.GET.get("page", 1)
    try:
        page_number = int(page_number)
    except:
        page_number = 1

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_pages": paginator.num_pages,
        "current_page": page_number,
        "page_title": "歌手列表",
    }
    return render(request, "music/artist_list.html", context)


def artist_detail(request, artist_id):
    """歌手详情页"""
    artist = get_object_or_404(Artist, id=artist_id)
    songs = Song.objects.filter(artist=artist.name).order_by("title")

    context = {"artist": artist, "songs": songs, "page_title": artist.name}
    return render(request, "music/artist_detail.html", context)


def search(request):
    """搜索页"""
    return render(request, "music/search.html", {"page_title": "搜索"})


def search_results(request):
    """搜索结果页"""
    query = request.GET.get("q", "").strip()
    search_type = request.GET.get("type", "song")
    search_field = request.GET.get("field", "all")  # 新增：搜索字段

    if not query:
        return redirect("search")

    start_time = time.time()
    results = []
    total_count = 0

    if search_type == "song":
        # 根据选择的字段搜索歌曲
        if search_field == "title":
            songs = Song.objects.filter(title__icontains=query).distinct()
        elif search_field == "artist":
            songs = Song.objects.filter(artist__icontains=query).distinct()
        elif search_field == "lyric":
            songs = Song.objects.filter(lyric__icontains=query).distinct()
        else:  # search_field == "all"
            songs = Song.objects.filter(
                Q(title__icontains=query)
                | Q(artist__icontains=query)
                | Q(lyric__icontains=query)
            ).distinct()
        results = songs
        total_count = songs.count()
    else:  # search_type == 'artist'
        # 根据选择的字段搜索歌手
        if search_field == "name":
            artists = Artist.objects.filter(name__icontains=query).distinct()
        elif search_field == "abstract":
            artists = Artist.objects.filter(abstract__icontains=query).distinct()
        else:  # search_field == "all"
            artists = Artist.objects.filter(
                Q(name__icontains=query) | Q(abstract__icontains=query)
            ).distinct()
        results = artists
        total_count = artists.count()

    search_time = time.time() - start_time

    # 分页
    paginator = Paginator(results, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "search_type": search_type,
        "search_field": search_field,  # 新增：传递搜索字段到模板
        "total_count": total_count,
        "search_time": round(search_time, 3),
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "page_title": f"搜索结果: {query}",
    }
    return render(request, "music/search_results.html", context)


@require_POST
@csrf_protect
def add_comment(request, song_id):
    # 使用 get_object_or_404 确保歌曲存在
    song = get_object_or_404(Song, id=song_id)

    content = request.POST.get("content", "").strip()
    if not content:
        messages.error(request, "评论内容不能为空！")
        return redirect("song_detail", song_id=song_id)

    try:
        Comment.objects.create(
            song=song,  # 使用歌曲对象而不是ID
            content=content,
        )
        messages.success(request, "评论添加成功！")
    except Exception as e:
        messages.error(request, f"添加评论失败：{str(e)}")

    return redirect("song_detail", song_id=song_id)


@require_POST
@csrf_protect
def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        song_id = comment.song.id
        comment.delete()
        messages.success(request, "评论删除成功！")
    except Exception as e:
        messages.error(request, f"删除评论失败：{str(e)}")
        # 如果无法获取song_id，尝试从referer获取
        referer = request.META.get("HTTP_REFERER", "/")
        if "/song/" in referer:
            return redirect(referer)
        return redirect("song_list")

    return redirect("song_detail", song_id=song_id)
