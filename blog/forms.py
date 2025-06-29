# blog/forms.py
from django import forms
from .models import Blog, Client

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        # 'place_name' 필드를 fields 목록에서 제거
        fields = ['client', 'content'] # image_url, client_type은 Client 모델로, place_name은 여기서 제거
        widgets = {
            'client': forms.Select(attrs={ # 클라이언트를 드롭다운으로 선택
                'class': 'form-select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '1000자 이상의 내용을 입력하세요'
            }),
            # 'place_name' 위젯 설정 제거
            # 'place_name': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '장소명'
            # }),
        }
        labels = {
            'client': '클라이언트',
            'content': '내용',
            # 'place_name' 라벨 설정 제거
            # 'place_name': '장소명',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Client 드롭다운에 표시될 텍스트 설정 (없을 경우를 대비)
        self.fields['client'].queryset = Client.objects.all().order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 1000:
            raise forms.ValidationError('내용은 1000자 이상이어야 합니다.')
        return content

