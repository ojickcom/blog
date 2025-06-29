# blog/forms.py
from django import forms
from .models import Blog, Client

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        # 'b_title' 필드를 fields 목록에 추가
        fields = ['client', 'b_title', 'title', 'content'] 
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select',
            }),
            'b_title': forms.TextInput(attrs={ # b_title 입력 필드 추가
                'class': 'form-control',
                'placeholder': 'B_제목을 입력하세요 (선택 사항)'
            }),
            'title': forms.TextInput(attrs={ 
                'class': 'form-control',
                'placeholder': '블로그 제목을 입력하세요 (비워두면 자동 생성)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '1000자 이상의 내용을 입력하세요'
            }),
        }
        labels = {
            'client': '클라이언트',
            'b_title': 'B_제목', # B_제목 라벨 추가
            'title': '제목', 
            'content': '내용',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 1000:
            raise forms.ValidationError('내용은 1000자 이상이어야 합니다.')
        return content

