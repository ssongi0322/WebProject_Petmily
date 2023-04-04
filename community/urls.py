from django.urls import path
from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    ### post
    path("post/write/", views.post_write, name="post_write"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("post/edit/<int:post_id>/", views.post_edit, name="post_edit"),
    path("post/delete/<int:post_id>/", views.post_delete, name="post_delete"),
    # path("post/like/", views.post_like, name='post_like'),
    ### answer
    path("answer/write/<int:post_id>/", views.answer_write, name="answer_write"),
    path("answer/edit/<int:answer_id>/", views.answer_edit, name="answer_edit"),
    path("answer/delete/<int:answer_id>/", views.answer_delete, name="answer_delete"),
    ### comment
    path(
        "comment/write/answer/<int:answer_id>/",
        views.comment_write,
        name="comment_write",
    ),
    path(
        "comment/edit/answer/<int:comment_id>/", views.comment_edit, name="comment_edit"
    ),
    path(
        "comment/delete/answer/<int:comment_id>/",
        views.comment_delete,
        name="comment_delete",
    ),
    ### vote
    # http://127.0.0.1:8000/board/question/vote/1/
    path("question/vote/<int:post_id>/", views.vote_post, name="vote_post"),
    path("answer/vote/<int:answer_id>/", views.vote_answer, name="vote_answer"),
    path("comment/vote/<int:comment_id>/", views.vote_comment, name="vote_comment"),
    
]
