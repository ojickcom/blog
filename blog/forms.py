# blog/forms.py
from django import forms
from .models import Blog, Client, ShoppingKeyword
from django.forms.widgets import Select # forms.Select 위젯을 직접 임포트

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

# SubKeywordAddForm: 기존 메인 키워드에 하위 키워드를 연결 (모달용)
# 이 폼은 기존 메인 키워드를 선택하고 그 아래에 하위 키워드를 입력받습니다.
class SubKeywordAddForm(forms.ModelForm):
    KEYWORD_GROUP_CHOICES = [
        ('그룹1', '그룹1'),
        ('그룹2', '그룹2'),
        ('그룹3', '그룹3'),
        ('그룹4', '그룹4'),
        ('그룹5', '그룹5'),
        ('기본', '기본'), # '기본' 옵션 추가 (모델의 default와 일치하도록)
    ]
    keyword_group = forms.ChoiceField(
        choices=KEYWORD_GROUP_CHOICES,
        label="키워드 그룹",
        widget=Select(attrs={'class': 'form-select'}) # forms.Select 대신 Select 사용
    )

    class Meta:
        model = ShoppingKeyword
        # client, main_keyword (ModelChoiceField로 변경 필요), keyword, keyword_group
        fields = ['client', 'main_keyword', 'keyword', 'keyword_group']
        labels = {
            'client': '클라이언트',
            'main_keyword': '상위 메인 키워드', # 기존 메인 키워드를 선택합니다.
            'keyword': '하위 키워드 이름',
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'client': Select(attrs={'class': 'form-select'}), # forms.Select 대신 Select 사용
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이 상위 키워드에 연결될 하위 키워드 이름을 입력하세요'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"
        
        # main_keyword 필드를 ModelChoiceField로 변경하여 실제 ShoppingKeyword 객체를 선택하도록 합니다.
        # 이 필드는 main_keyword가 NULL인 (즉, 스스로 메인 키워드인) 객체만 선택지로 제공합니다.
        self.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(main_keyword__isnull=True).order_by('keyword')
        self.fields['main_keyword'].empty_label = "--- 상위 메인 키워드를 선택하세요 ---"

    def clean(self):
        cleaned_data = super().clean()
        keyword = cleaned_data.get('keyword')
        client = cleaned_data.get('client')
        main_keyword = cleaned_data.get('main_keyword')

        if client and keyword and main_keyword:
            if ShoppingKeyword.objects.filter(client=client, keyword=keyword, main_keyword=main_keyword).exists():
                raise forms.ValidationError(f"'{keyword}' 키워드는 이미 '{main_keyword.keyword}'의 하위 키워드로 존재합니다.")
        elif main_keyword is None:
            # 이 경우 main_keyword는 ModelChoiceField이므로, 실제로 값이 없는 경우를 처리합니다.
            # empty_label이 설정되어 있으므로, 선택 안하면 이 에러가 발생합니다.
            raise forms.ValidationError("상위 메인 키워드를 반드시 선택해야 합니다.")
        
        return cleaned_data


# MainKeywordAddForm: 완전히 새로운 메인 키워드 생성 (페이지 이동용)
# 이 폼은 keyword 필드에 새로운 메인 키워드 이름을 입력받고, main_keyword 필드는 NULL로 저장됩니다.
class MainKeywordAddForm(forms.ModelForm):
    KEYWORD_GROUP_CHOICES = [
        ('그룹1', '그룹1'),
        ('그룹2', '그룹2'),
        ('그룹3', '그룹3'),
        ('그룹4', '그룹4'),
        ('그룹5', '그룹5'),
        ('기본', '기본'), # '기본' 옵션 추가
    ]
    keyword_group = forms.ChoiceField(
        choices=KEYWORD_GROUP_CHOICES,
        label="키워드 그룹",
        widget=Select(attrs={'class': 'form-select'}) # forms.Select 대신 Select 사용
    )

    class Meta:
        model = ShoppingKeyword
        # 여기서는 'keyword' 필드에 메인 키워드 이름을 입력받습니다.
        # 'main_keyword' 필드는 이 폼에서 사용하지 않습니다 (None으로 저장될 것이기 때문에).
        fields = ['client', 'keyword', 'keyword_group'] 
        labels = {
            'client': '클라이언트',
            'keyword': '새로운 메인 키워드 이름', # 레이블을 명확히 변경
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'client': Select(attrs={'class': 'form-select'}), # forms.Select 대신 Select 사용
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '새로운 메인 키워드 이름을 입력하세요'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        self.fields['client'].empty_label = "--- 클라이언트를 선택하세요 ---"
        # self.fields['keyword_group'].initial = '기본' # 이제 필요 없습니다.

    def clean_keyword(self): # main_keyword 대신 keyword 필드에 대한 유효성 검사
        keyword = self.cleaned_data['keyword']
        client = self.cleaned_data.get('client')
        # 새로운 메인 키워드는 client-keyword 조합이 유일해야 함 (main_keyword가 NULL인 경우)
        if client and ShoppingKeyword.objects.filter(client=client, keyword=keyword, main_keyword__isnull=True).exists():
            raise forms.ValidationError(f"'{keyword}' 메인 키워드는 이미 이 클라이언트에 존재합니다. 다른 이름을 사용해주세요.")
        return keyword

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 새로운 메인 키워드이므로 main_keyword 필드는 항상 NULL로 설정
        instance.main_keyword = None 
        if commit:
            instance.save()
        return instance