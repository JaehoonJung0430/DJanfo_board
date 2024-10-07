from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Post
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer

def HTMLTemplate(articleTag, id=None, posts=None):
    contextUI = ''
    if id is not None:
        contextUI = f'''
            <li><a class="button" href="/">글 목록</a></li>
            <li>
                <form action="/delete/" method="post" style="display:inline;">
                    <input type="hidden" name="id" value={id}>
                    <input type="submit" value="삭제" class="button delete" onclick="return confirm('정말 삭제하시겠습니까?');">
                </form>
            </li>
            <li><a class="button" href='/update/{id}'>수정</a></li>
        '''

    ol = ''
    if posts is not None:
        for post in posts:
            ol += f'''
                <div class="post-box">
                    <h3><a href="/read/{post.id}">{post.title}</a></h3>
                    <p>{post.body[:50]}...</p>
                </div>
            '''
    
    return f'''
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            .post-box {{
                border: 1px solid #ccc;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                background-color: white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .button {{
                padding: 12px 20px;
                font-size: 16px;
                background-color: #007BFF;
                color: white;
                border: none;
                text-decoration: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
                margin-right: 20px;
                margin-bottom: 15px;
                display: inline-block;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
            .button.delete {{
                background-color: #dc3545;
            }}
            .button.delete:hover {{
                background-color: #c82333;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
            }}
            .time-info {{
                font-size: 12px;
                color: #666;
            }}
            .article-title {{
                font-size: 24px;
                font-weight: bold;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            .article-body {{
                border: 1px solid #ccc;
                padding: 15px;
                background-color: white;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .form-title {{
                font-size: 24px;
                font-weight: bold;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            .form-body {{
                border: 1px solid #ccc;
                padding: 15px;
                background-color: white;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1><a href="/">Django로 만든 게시판</a></h1>
            <ul>
                <li><a class="button" href="/create/">글 작성</a></li>
            </ul>
            <div>{articleTag}</div>
            <ul>
                {ol}
            </ul>
            <ul>
                {contextUI}
            </ul>
        </div>
    </body>
    </html>
    '''

def index(request):
    posts = Post.objects.all().order_by('-created_at')
    article = '<h2>글 목록</h2>'
    return HttpResponse(HTMLTemplate(article, posts=posts))

def read(request, id):
    post = get_object_or_404(Post, pk=id)
    article = f'''
        <div class="article-title">{post.title}</div>
        <div class="time-info">작성 시간: {post.created_at} | 수정 시간: {post.updated_at}</div>
        <div class="article-body">{post.body}</div>
    '''
    return HttpResponse(HTMLTemplate(article, id=post.id))

@csrf_exempt
def create(request):
    if request.method == 'GET':
        article = '''
            <h2>글 작성</h2>
            <div class="form-title">제목</div>
            <form action="/create/" method="post">
                <p><input type="text" name="title" placeholder="제목" required></p>
                <div class="form-body">
                    <textarea name="body" placeholder="내용" required></textarea>
                </div>
                <p>
                    <input type="submit" value="작성 완료" class="button">
                    <a class="button" href="/">취소</a>
                </p>
            </form>
        '''
        return HttpResponse(HTMLTemplate(article))
    elif request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        Post.objects.create(title=title, body=body)
        return redirect('/')

@csrf_exempt
def update(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.method == 'GET':
        article = f'''
            <h2>글 수정</h2>
            <div class="form-title">제목</div>
            <form action="/update/{id}/" method="post">
                <p><input type="text" name="title" value="{post.title}" required></p>
                <div class="form-body">
                    <textarea name="body" required>{post.body}</textarea>
                </div>
                <p>
                    <input type="submit" value="수정 완료" class="button">
                    <a class="button" href="/">취소</a>
                </p>
            </form>
        '''
        return HttpResponse(HTMLTemplate(article, id=post.id))
    elif request.method == 'POST':
        post.title = request.POST['title']
        post.body = request.POST['body']
        post.updated_at = timezone.now()
        post.save()
        return redirect(f'/read/{id}')

@csrf_exempt
def delete(request):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=request.POST['id'])
        post.delete()
        return redirect('/')

# API Views
class PostListCreateAPIView(APIView):
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

    def get(self, request, id):
        post = self.get_object(id)
        if post is None:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, id):
        post = self.get_object(id)
        if post is None:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        post = self.get_object(id)
        if post is None:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
