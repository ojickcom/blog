# blog/forms.py
from django import forms
from .models import Blog, Client, ShoppingKeyword

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['client', 'b_title', 'title', 'content']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select',
            }),
            'b_title': forms.TextInput(attrs={
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
            'b_title': 'B_제목',
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

# 이 폼은 이미 keyword_group을 선택할 수 있도록 되어 있습니다.
class ShoppingKeywordForm(forms.ModelForm):
    # 키워드 그룹 선택 필드 정의
    KEYWORD_GROUP_CHOICES = [
        ('그룹1', '그룹1'),
        ('그룹2', '그룹2'),
        ('그룹3', '그룹3'),
        ('그룹4', '그룹4'),
        ('그룹5', '그룹5'),
    ]
    keyword_group = forms.ChoiceField( # 이미 ChoiceField로 정의되어 있음
        choices=KEYWORD_GROUP_CHOICES,
        label="키워드 그룹",
        widget=forms.Select(attrs={'class': 'form-select'}) # Bootstrap 스타일 적용
    )

    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'main_keyword', 'keyword_group']
        labels = {
            'client': '클라이언트',
            'keyword': '키워드',
            'main_keyword': '메인 키워드',
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}), # Bootstrap 스타일 추가
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '키워드를 입력하세요'}),
            # main_keyword는 현재 TextInput으로 되어 있습니다.
            # 만약 기존 메인 키워드를 선택하게 하려면 ModelChoiceField로 변경해야 합니다.
            # 지금은 텍스트 입력으로 가정하고, Bootstrap 스타일만 추가합니다.
            'main_keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '메인 키워드를 입력하세요 (선택사항)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"


# MainShoppingKeywordForm의 keyword_group을 선택할 수 있도록 수정
class MainShoppingKeywordForm(forms.ModelForm):
    # ShoppingKeywordForm과 동일한 선택지를 사용하거나, 모델 필드에 직접 정의된 choices를 사용
    # 여기서는 동일한 선택지 리스트를 복사하여 사용합니다.
    KEYWORD_GROUP_CHOICES = [
        ('그룹1', '그룹1'),
        ('그룹2', '그룹2'),
        ('그룹3', '그룹3'),
        ('그룹4', '그룹4'),
        ('그룹5', '그룹5'),
    ]
    keyword_group = forms.ChoiceField( # ChoiceField로 변경
        choices=KEYWORD_GROUP_CHOICES,
        label="키워드 그룹",
        widget=forms.Select(attrs={'class': 'form-select'}) # Select 위젯 적용
    )

    class Meta:
        model = ShoppingKeyword
        # fields에 keyword_group 포함
        fields = ['client', 'main_keyword', 'keyword_group'] 
        labels = {
            'client': '클라이언트',
            'main_keyword': '메인 키워드 이름',
            'keyword_group': '키워드 그룹', # 레이블 다시 활성화
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}), # Bootstrap 스타일 추가
            'main_keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '메인 키워드 이름을 입력하세요'}),
            # keyword_group 위젯은 위에서 forms.ChoiceField에 직접 정의했으므로 여기서는 제거
            # 'keyword_group': forms.HiddenInput(), # 이 줄은 삭제
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"
        # 이제 HiddenInput이 아니므로 initial 값을 강제로 설정할 필요가 없습니다.
        # self.fields['keyword_group'].initial = '기본' # 이 줄은 삭제 또는 필요에 따라 기본 선택지 설정

    def clean_main_keyword(self):
        main_keyword = self.cleaned_data['main_keyword']
        client = self.cleaned_data.get('client')

        # main_keyword 기준 중복 검사
        if client and ShoppingKeyword.objects.filter(client=client, main_keyword=main_keyword).exists():
            raise forms.ValidationError(f"'{main_keyword}' 메인 키워드는 이미 이 클라이언트에 존재합니다.")
        return main_keyword

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.keyword = instance.main_keyword  # keyword에도 메인 키워드 이름을 복사
        if commit:
            instance.save()
        return instance