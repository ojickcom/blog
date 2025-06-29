# blog/forms.py

from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        # 이전에 Blog 모델에서 제거한 필드들을 여기서도 제거합니다.
        fields = ['content', 'client_type', 'image_url', 'place_name'] # 여기를 수정!
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '1000자 이상의 내용을 입력하세요'
            }),
            'client_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '클라이언트 타입'
            }),
            'image_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '이미지 URL'
            }),
            'place_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '장소명'
            }),
            # 아래 주석 처리된(혹은 삭제된) 위젯들도 모두 제거해야 합니다.
            # 'content_title': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '컨텐츠 제목'
            # }),
            # 'content_number_character': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '글자 수 특성'
            # }),
            # 'content_talkstyle': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '말투 스타일'
            # }),
            # 'content_aspect': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '컨텐츠 관점'
            # }),
        }
        labels = {
            'content': '내용',
            'client_type': '클라이언트 타입',
            'image_url': '이미지 URL',
            'place_name': '장소명',
            # 아래 주석 처리된(혹은 삭제된) 라벨들도 모두 제거해야 합니다.
            # 'content_title': '컨텐츠 제목',
            # 'content_number_character': '글자 수 특성',
            # 'content_talkstyle': '말투 스타일',
            # 'content_aspect': '컨텐츠 관점',
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 1000:
            raise forms.ValidationError('내용은 1000자 이상이어야 합니다.')
        return content