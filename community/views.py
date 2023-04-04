from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from .models import Post, PostCount, Answer, Comment, Image
from .forms import PostForm, AnswerForm, CommentForm, ImageForm

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.db.models import Q, Count
from tools.utils import get_client_ip

from django.contrib import messages

from django.forms import modelformset_factory


##### post #####

# 리스트
def post_list(request):

    post_list = Post.objects.order_by("-created_at")

    # 검색조건,검색어 받기
    search_kind = request.GET.get("search_kind", "")
    keyword = request.GET.get("keyword", "")

    # 정렬기준 받기
    so = request.GET.get("so", "recent")

    # 정렬
    if so == "recommend":
        # 추천 많은 순서
        post_list = Post.objects.annotate(num_vote=Count("vote")).order_by(
            "-num_vote", "-created_at"
        )
    elif so == "popular":
        # 답변 많은 순서
        post_list = Post.objects.annotate(num_answer=Count("answer")).order_by(
            "-num_answer", "-created_at"
        )
    else:
        # 최신글부터
        post_list = Post.objects.order_by("-created_at")

    if keyword:
        if len(keyword) > 1:
            if search_kind == 'all':
                post_list = post_list.filter(
                    Q(title__icontains=keyword) | 
                    Q(content__icontains=keyword) | 
                    Q(writer__email__icontains=keyword)).distinct()
            elif search_kind == "title":
                post_list = post_list.filter(
                    title__icontains=keyword).distinct()
            elif search_kind == "writer":
                post_list = post_list.filter(
                    writer__email__icontains=keyword).distinct()
            elif search_kind == "content":
                post_list = post_list.filter(
                    content__icontains=keyword).distinct()
        else:
            messages.error(request, "검색어는 2글자 이상 입력해주세요.")

    # 페이지
    page = request.GET.get("page", 1)

    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page)

    return render(
        request,
        "community/post_list.html",
        {
            "post_list": page_obj,
            "page": page,
            "so": so,
            "keyword": keyword,
            "search_kind": search_kind,
        },
    )


# 글작성
@login_required(login_url="login")
def post_write(request):

    # 하나의 modelform 을 여러번 쓸 수 있음. 모델, 모델폼, 몇 개의 폼을 띄울건지 갯수
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=5)

    if request.method == 'POST':

        postForm = PostForm(request.POST)
        # queryset 을 none 으로 정의해서 이미지가 없어도 되도록 설정. none 은 빈 쿼리셋 리턴
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=Image.objects.none())

        # 두 모델폼의 유효성 검사를 해주고
        if postForm.is_valid() and formset.is_valid():
            post_form = postForm.save(commit=False)
            post_form.writer = request.user
            post_form.save()

            # 유효성 검사가 왼료된 formset 정리된 데이터 모음
            for form in formset.cleaned_data:
                if form:
                    # image file
                    image = form['image']
                    print(form)
                    print(form['image'])
                    # post, image file save
                    photo = Image(post=post_form, image=image)
                    photo.save()
            return redirect('post_list')
        # 유효성 검사 실패시 터미널상에 에러메시지 print
        else:
            print(postForm.errors, formset.errors)
    else:
        # POST 요청이 아닌 경우
        postForm = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'community/post_write.html',
                  {'postForm': postForm, 'formset': formset})


# 상세내용
def post_detail(request, post_id):

    page = request.GET.get("page", 1)
    keyword = request.GET.get("keyword", "")
    so = request.GET.get("so", "recent")

    post = get_object_or_404(Post, id=post_id)

    # 조회수
    ip = get_client_ip(request)
    cnt = PostCount.objects.filter(ip=ip, post=post).count()

    if cnt == 0:
        post_cnt = PostCount(ip=ip, post=post)
        post_cnt.save()

        if post.view_cnt:
            post.view_cnt += 1
        else:
            post.view_cnt = 1
        post.save()

    return render(
        request,
        "community/post_detail.html",
        {"post": post, "page": page, "keyword": keyword, "so": so},
    )
    


# 수정
@login_required(login_url="login")
def post_edit(request, post_id):
    """
    이미 이미지가 있는 경우
    1. 이미지가 새롭게 들어오는 경우 - 기존 이미지 제거 후 새로운 이미지 삽입
    2. 이미지가 안들어오는 경우 - 기존 이미지 유지


    기존 내용에 이미지가 없는 경우
    1. 이미지가 새롭게 들어오는 경우 - (기존 이미지 제거 후) 새로운 이미지 삽입
    """

    post = get_object_or_404(Post, id=post_id)
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=5)

    if request.method == 'POST':

        postForm = PostForm(request.POST, instance=post)
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=Image.objects.none())

        # 두 모델폼의 유효성 검사
        if postForm.is_valid() and formset.is_valid():
            post_form = postForm.save(commit=False)
            post_form.writer = request.user
            post_form.save()
            print("수정된 모델", post_form)

            # 처음에 보낸 폼과 내용이 달라진 경우 실행
            if formset.has_changed():
                files = Image.objects.filter(post=post_form)
                files.delete()

            # 이미지가 새롭게 들어오는 경우
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = Image(post=post_form, image=image)
                    photo.save()
            return redirect("post_detail", post_id=post_id)
        # 유효성 검사 실패시 터미널상에 에러메시지 print
        else:
            print(postForm.errors, formset.errors)
    else:
        # POST 요청이 아닌 경우
        postForm = PostForm(instance=post)
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'community/post_edit.html',
                  {'postForm': postForm, 'formset': formset})


# 삭제
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect("post_list")


##### answer #####

# 댓글 등록
@login_required(login_url="login")
def answer_write(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.post = post
            answer.writer = request.user
            answer.save()
            return redirect(
                "{}#answer_{}".format(
                    resolve_url("post_detail", post_id=post_id), answer.id
                )
            )
    else:
        form = AnswerForm()
    return render(request, "community/post_detail.html", {"form": form, "post": post})


# 댓글 수정
def answer_edit(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.save()
            return redirect(
                "{}#answer_{}".format(
                    resolve_url("post_detail",
                                post_id=answer.post_id), answer.id
                )
            )
    else:
        form = AnswerForm(instance=answer)

    return render(request, "community/answer_form.html", {"form": form})


# 댓글 삭제
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    answer.delete()
    return redirect("post_detail", post_id=answer.post_id)


##### comment #####

# 대댓글 등록
@login_required(login_url="login")
def comment_write(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.answer = answer
            comment.writer = request.user
            comment.save()
            return redirect(
                "{}#comment_{}".format(
                    resolve_url("post_detail",
                                post_id=answer.post.id), comment.id
                )
            )
    else:
        form = CommentForm()

    return render(
        request, "community/comment_form.html", {
            "form": form, "answer": answer}
    )


# 대댓글 수정
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            return redirect(
                "{}#answer_{}".format(
                    resolve_url("post_detail", post_id=comment.answer.post.id),
                    comment.id,
                )
            )
    else:
        form = CommentForm(instance=comment)

    return render(request, "community/comment_form.html", {"form": form})


# 대댓글 삭제
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect("post_detail", post_id=comment.answer.post_id)


##### 추천 #####


@login_required(login_url="login")
def vote_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # 질문 찾은 후 question.voter.add(로그인 사용자)
    # 자신의 글은 추천하지 못하도록
    if post.writer != request.user:
        post.vote.add(request.user)
    else:
        messages.error(request, "본인이 작성한 글은 추천할 수 없습니다.")

    return redirect("post_detail", post_id=post_id)


@login_required(login_url="login")
def vote_answer(request, answer_id):

    answer = get_object_or_404(Answer, id=answer_id)

    if answer.writer != request.user:
        answer.vote.add(request.user)
    else:
        messages.error(request, "본인이 작성한 글은 추천할 수 없습니다.")

    return redirect("post_detail", post_id=answer.post.id)


@login_required(login_url="login")
def vote_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    if comment.writer != request.user:
        comment.vote.add(request.user)
    else:
        messages.error(request, "본인이 작성한 글은 추천할 수 없습니다.")

    return redirect("post_detail", post_id=comment.answer.post.id)
