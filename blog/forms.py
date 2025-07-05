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
    # main_keyword 필드에 대한 쿼리셋을 동적으로 설정 (자기 자신을 제외한 키워드만 선택 가능)
    # 이 부분은 __init__에서 처리하는 것이 더 좋습니다.
    # 일단은 모든 ShoppingKeyword를 보여주도록 설정하고,
    # 템플릿이나 뷰에서 현재 편집 중인 키워드를 제외하는 로직을 추가할 수 있습니다.
    main_keyword = forms.ModelChoiceField(
        queryset=ShoppingKeyword.objects.all(),
        required=False, # 메인 키워드가 없을 수도 있으므로 필수 아님
        label="메인 키워드",
        help_text="이 키워드가 종속될 메인 키워드를 선택하세요."
    )

    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'main_keyword', 'is_click_target']
        labels = {
            'client': '클라이언트',
            'keyword': '키워드',
            'is_click_target': '클릭 대상 키워드',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 폼 인스턴스 (즉, 수정 모드)일 경우, main_keyword 선택지에서 자기 자신을 제외
        if self.instance and self.instance.pk:
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.exclude(pk=self.instance.pk)
        else: # 생성 모드일 경우 모든 키워드 보여줌
             self.fields['main_keyword'].queryset = ShoppingKeyword.objects.all()

        # 클라이언트 선택 드롭다운에 모든 클라이언트 표시 (이전에 이미 있을 것)
        self.fields['client'].queryset = Client.objects.all()