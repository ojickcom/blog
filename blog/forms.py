# blog/forms.py
from django import forms
from .models import Blog, Client,  ShoppingKeyword

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
                'placeholder': '10자 이상의 내용을 입력하세요'
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
        if len(content) < 50:
            raise forms.ValidationError('내용은 50자 이상이어야 합니다.')
        return content
class ShoppingKeywordForm(forms.ModelForm):
    # main_keyword 필드는 ModelChoiceField로 유지
    main_keyword = forms.ModelChoiceField(
        queryset=ShoppingKeyword.objects.all(),
        required=False,
        label="메인 키워드",
        help_text="이 키워드가 종속될 메인 키워드를 선택하세요."
    )
    
    # keyword_group 필드를 CharField로 추가
    keyword_group = forms.CharField(
        max_length=50,
        required=True,
        initial='기본', # 폼 초기값 설정
        label="키워드 그룹",
        help_text="이 키워드가 속할 그룹을 입력하세요 (예: keyword_group1, keyword_group2)"
    )

    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'main_keyword', 'keyword_group'] # is_click_target 제거
        labels = {
            'client': '클라이언트',
            'keyword': '키워드',
            # 'keyword_group' 라벨은 이미 필드 정의에서 설정됨
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 수정 모드일 때 main_keyword 선택지에서 자기 자신을 제외
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.exclude(pk=self.instance.pk)
        else:
            # 생성 모드일 때 모든 키워드를 main_keyword로 선택 가능
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.all()

        self.fields['client'].queryset = Client.objects.all()