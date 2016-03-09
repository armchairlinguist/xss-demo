from pyramid.view import view_config
from pyramid.request import Response
import pyramid.httpexceptions as exc
import html

from .models import (
    DB,
    Post,
    Comment,
    )


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    posts = DB.get_all(Post)
    return {'posts': sorted(posts, key=lambda post: post.date, reverse=True)}


@view_config(route_name='post', renderer='templates/post.pt')
def post(request):
    post_id = int(request.matchdict['id'])
    post = DB.get(Post, post_id)
    comments = []
    for cid in post.comment_ids:
        comments.append(DB.get(Comment, cid))
    return {
        'post': post,
        'comments': sorted(comments, key=lambda comment: comment.date,
                           reverse=True)
         }


@view_config(route_name='add_comment')
def add_comment(request):
    post_id = int(request.matchdict['id'])
    post = DB.get(Post, post_id)
    author = request.params['author']
    message = request.params['message']
    comment = Comment(message, author, post_id)
    DB.save(comment)
    post.comment_ids.append(comment.id)
    DB.save(post)
    raise exc.HTTPFound(request.route_url('post', id=post_id))


@view_config(route_name='new_post', renderer='templates/new_post.pt')
def new_post(request):
    return {}


@view_config(route_name='add_post')
def add_post(request):
    author = 'authenticated userid'
    title = request.params['title']
    content = request.params['content']
    post = Post(title, content, author)
    DB.save(post)
    raise exc.HTTPFound(request.route_url('post', id=post.id))


@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    return {}


@view_config(route_name='authenticate')
def authenticate(request):
    username = request.params['username']
    password = request.params['password']
    # authenticate
    # set cookie
    raise exc.HTTPFound(request.route_url('home'))


@view_config(route_name='search', renderer='templates/search.pt')
def search(request):
    return {'query': request.params.get('q', '')}
    # http://localhost:6543/search?q=%3Cscript%3Ealert(123)%3C/script%3E
    # chromium-browser --temp-profile --disable-xss-auditor


@view_config(route_name='search_raw')
def search_raw(request):
    """
    Search results without template (raw Response() object).
    Templates help escaping characters.
    """
    query = request.params.get('q', '')
    #query = html.escape(query)
    content = """
<html>
    <body>
        <p>Your query is: {0}</p>
    </body>
</html>""".format(query)
    return Response(content)
