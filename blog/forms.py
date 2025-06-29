from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [
            'content', 'client_type', 'image_url', 'place_name',
            'content_title', 'content_number_character', 
            'content_talkstyle', 'content_aspect'
        ]
        
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': '1000자 이상의 내용을 입력하세요...',
                'required': True
            }),
            'client_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '클라이언트 타입 (예: 개인, 기업, 단체)',
                'maxlength': 20,
                'required': True
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg',
                'maxlength': 50,
                'required': True
            }),
            'place_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '장소명 (예: 서울, 부산)',
                'maxlength': 20,
                'required': True
            }),
            'content_title': forms.TextInput(attrs={
                'class': 'form-control title-component',
                'placeholder': '컨텐츠 제목 키워드',
                'maxlength': 20,
                'required': True
            }),
            'content_number_character': forms.TextInput(attrs={
                'class': 'form-control title-component',
                'placeholder': '글자 수 특성 (예: 짧은, 긴)',
                'maxlength': 20,
                'required': True
            }),
            'content_talkstyle': forms.TextInput(attrs={
                'class': 'form-control title-component',
                'placeholder': '말투 스타일 (예: 친근한, 전문적인)',
                'maxlength': 20,
                'required': True
            }),
            'content_aspect': forms.TextInput(attrs={
                'class': 'form-control title-component',
                'placeholder': '컨텐츠 관점 (예: 실용적, 감성적)',
                'maxlength': 20,
                'required': True
            }),
        }
        
        labels = {
            'content': '본문 내용',
            'client_type': '클라이언트 타입',
            'image_url': '이미지 URL',
            'place_name': '장소명',
            'content_title': '컨텐츠 제목',
            'content_number_character': '글자 수 특성',
            'content_talkstyle': '말투 스타일',
            'content_aspect': '컨텐츠 관점',
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if len(content) < 1000:
            raise forms.ValidationError(f'내용은 1000자 이상이어야 합니다. (현재: {len(content)}자)')
        return content
    
    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url', '')
        if not image_url.startswith(('http://', 'https://')):
            raise forms.ValidationError('올바른 URL 형식을 입력해주세요.')
        return image_url
