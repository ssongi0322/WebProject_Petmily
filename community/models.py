from django.db import models
from user.models import User
from django.db.models import UniqueConstraint
from django.template.defaultfilters import slugify
from django.urls import reverse

class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='작성날짜', auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name='수정날짜', auto_now=True)
    
    class Meta:
        abstract = True
    
    
class Post(BaseModel):
    title = models.CharField(max_length=200, verbose_name='제목')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자', related_name='writer_post')
    content = models.TextField(verbose_name='내용')
    view_cnt = models.BigIntegerField(default=0)
    vote = models.ManyToManyField(User, related_name='vote_post', verbose_name='추천수')
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("post_detail", args=[self.pk])
    
    def get_previous(self):
        return self.get_previous_by_created_at()
    
    def get_next(self):
        return self.get_next_by_created_at()
    
    
# image file naming
# instance => 현재 정의된 모델의 인스턴스 
# filename => 파일에 원래 제공된 파일 이름. 이것은 최종 목적지 경로를 결정할 때 고려되거나 고려되지 않을 수 있음
def image_upload_to(instance, filename):
    # 해당 Post 모델의 title 을 가져옴
    title = instance.post.title
    # slug - 의미있는 url 사용을 위한 필드.
    # slugfy 를 사용해서 title을 slug 시켜줌.
    slug = slugify(title)
    # 제목 - 슬러그된 파일이름 형태
    return "post_images/%s-%s" % (slug, filename)


class Image(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="작성글", related_name="image")
    image = models.ImageField(upload_to=image_upload_to)

    class Meta:
        # 단수
        verbose_name = 'Image'
        # 복수
        verbose_name_plural = 'Images'

    # 이것도 역시 post title 로 반환
    def __str__(self):
       return str(self.post)


class PostCount(models.Model):
    ip = models.CharField(max_length=30)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    def __unicode__(self):
        return self.ip
    
    
class Answer(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='댓글')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자', related_name='writer_answer')
    vote = models.ManyToManyField(User, related_name='vote_answer', verbose_name='추천수')
    
    
class Comment(BaseModel):
    writer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자',related_name='writer_comment')
    content = models.TextField(verbose_name='대댓글')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    vote = models.ManyToManyField(User, related_name='vote_comment', verbose_name='추천수')
