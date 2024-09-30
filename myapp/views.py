from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

nextId = 1
topics = []

def HTMLTemplate(articleTag, id=None):
    global topics
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
    
    sorted_topics = sorted(topics, key=lambda x: x['created_at'], reverse=True)
    
    ol = ''
    for topic in sorted_topics:
        ol += f'''
            <div class="post-box">
                <h3><a href="/read/{topic["id"]}">{topic["title"]}</a></h3>
                <p>{topic["body"][:50]}...</p>
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
    article = '<h2>글 목록</h2>'
    return HttpResponse(HTMLTemplate(article))

def read(request, id):
    global topics
    article = ''
    for topic in topics:
        if topic['id'] == int(id):
            article = f'''
                <div class="article-title">{topic["title"]}</div>
                <div class="time-info">작성 시간: {topic["created_at"]} | 수정 시간: {topic["updated_at"]}</div>
                <div class="article-body">{topic["body"]}</div>
            '''
    return HttpResponse(HTMLTemplate(article, id))

@csrf_exempt
def create(request):
    global nextId
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
        newTopic = {
            "id": nextId,
            "title": title,
            "body": body,
            "created_at": timezone.now(),
            "updated_at": timezone.now()
        }
        topics.append(newTopic)
        nextId += 1
        return redirect('/')

@csrf_exempt
def delete(request):
    global topics
    if request.method == 'POST':
        id = request.POST['id']
        topics[:] = [topic for topic in topics if topic['id'] != int(id)]
        return redirect('/')

@csrf_exempt
def update(request, id):
    global topics
    if request.method == 'GET':
        for topic in topics:
            if topic['id'] == int(id):
                selectedTopic = {
                    "title": topic['title'],
                    "body": topic['body']
                }
        article = f'''
            <h2>글 수정</h2>
            <div class="form-title">제목</div>
            <form action="/update/{id}/" method="post">
                <p><input type="text" name="title" value="{selectedTopic["title"]}" required></p>
                <div class="form-body">
                    <textarea name="body" required>{selectedTopic['body']}</textarea>
                </div>
                <p>
                    <input type="submit" value="수정 완료" class="button">
                    <a class="button" href="/">취소</a>
                </p>
            </form>
        '''
        return HttpResponse(HTMLTemplate(article, id))
    elif request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        for topic in topics:
            if topic['id'] == int(id):
                topic['title'] = title
                topic['body'] = body
                topic['updated_at'] = timezone.now()
        return redirect(f'/read/{id}')
