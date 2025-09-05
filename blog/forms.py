# blog/forms.py
from django import forms
from .models import Blog, Client, ShoppingKeyword, KeywordGroup
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
                'rows': 40,
                'placeholder': '1000자 이상의 내용을 입력하세요'
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
KEYWORD_GROUP_CHOICES = [
    ('그룹1', '그룹1'),
    ('그룹2', '그룹2'),
    ('그룹3', '그룹3'),
    ('그룹4', '그룹4'),
    ('그룹5', '그룹5'),
    ('기타', '기타'), # 기타 그룹 추가
]
class MainKeywordInitialAddForm(forms.ModelForm):
    class Meta:
        model = ShoppingKeyword
        # 초기 메인 키워드 생성 시에는 client만 받습니다.
        # keyword와 keyword_group은 나중에 별도의 단계에서 추가됩니다.
        fields = ['client']
        labels = {
            'client': '클라이언트',
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().order_by('name')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.main_keyword = None  # 새 메인 키워드는 main_keyword가 None
        instance.keyword = "" # 초기 생성 시 keyword는 빈 문자열로 설정
        instance.keyword_group = "미지정" # 초기 생성 시 group은 '미지정'으로 설정
        if commit:
            instance.save()
        return instance

# 메인 키워드 이름과 그룹을 업데이트하는 폼 (2단계)
class MainKeywordInitialAddForm(forms.ModelForm):
    # groups 필드를 ModelMultipleChoiceField로 정의 (CheckboxSelectMultiple 위젯 사용)
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by('name'), # 모든 KeywordGroup 객체를 가져옴
        widget=forms.CheckboxSelectMultiple(), # 체크박스 형태로 표시
        required=False, # 필수가 아님
        label="키워드 그룹" # 폼 필드 레이블
    )

    class Meta:
        model = ShoppingKeyword
        # 여기에 'keyword' 필드를 추가해야 합니다.
        # 또한, main_keyword는 이 폼에서 설정하지 않으므로 포함하지 않습니다.
        fields = ['client', 'keyword', 'groups'] # <-- 'keyword'와 'groups' 필드를 추가
        labels = {
            'client': '클라이언트',
            'keyword': '메인 키워드 이름', # 레이블을 명확히 변경
            'groups': '키워드 그룹',
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '새로운 메인 키워드 이름을 입력하세요'}),
            # groups 필드는 위에서 widget을 직접 지정했으므로 여기에 다시 지정할 필요는 없습니다.
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 클라이언트 필드의 CSS 클래스를 추가합니다.
        self.fields['client'].queryset = Client.objects.all().order_by('name')
        self.fields['client'].empty_label = "클라이언트를 선택하세요"
        self.fields['client'].widget.attrs.update({'class': 'form-control'}) # 모든 클라이언트 필드에 적용

        # keyword 필드에 초기값이 없고 필수인 경우, placeholder를 추가합니다.
        # if 'keyword' in self.fields and self.instance.pk is None: # 새로운 인스턴스일 경우
        #     self.fields['keyword'].widget.attrs.update({'placeholder': '새로운 메인 키워드 이름을 입력하세요'})

class MainKeywordNameUpdateForm(forms.ModelForm):
    # keyword_group 대신 groups 필드를 ModelMultipleChoiceField로 변경
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by('name'), # 모든 KeywordGroup 객체를 선택지로 제공
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}), # 다중 선택을 위한 체크박스 위젯
        required=False, # 그룹 선택은 필수가 아님
        label="키워드 그룹"
    )

    class Meta:
        model = ShoppingKeyword
        # fields = ['keyword', 'keyword_group'] 대신 'groups' 사용
        fields = ['keyword', 'groups']
        labels = {
            'keyword': '메인 키워드 이름',
            'groups': '키워드 그룹',
        }
        widgets = {
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '메인 키워드 이름을 입력하세요'}),
        }

    # ManyToManyField는 save()만으로는 저장되지 않으므로 save_m2m()을 호출해야 함
    def save(self, commit=True):
        instance = super().save(commit)
        # 폼 데이터에서 groups 필드에 대한 변경사항을 인스턴스에 적용 (ManyToManyField용)
        if commit:
            self.save_m2m() # ManyToManyField 저장을 위해 필요
        return instance


# 하위 키워드 추가 폼
class SubKeywordAddForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="키워드 그룹 (선택)"
    )

    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'main_keyword', 'keyword', 'groups']
        labels = {
            'client': '클라이언트',
            'main_keyword': '상위 메인 키워드',
            'keyword': '서브 키워드',
            'groups': '키워드 그룹',
        }
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'main_keyword': forms.Select(attrs={'class': 'form-control'}),
            'keyword': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '서브 키워드를 입력하세요'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(main_keyword__isnull=True).exclude(keyword='').order_by('keyword')
