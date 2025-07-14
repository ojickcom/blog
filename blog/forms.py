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


class ShoppingKeywordForm(forms.ModelForm):
    # 키워드 그룹 선택 필드 정의
    KEYWORD_GROUP_CHOICES = [
        ('그룹1', '그룹1'),
        ('그룹2', '그룹2'),
        ('그룹3', '그룹3'),
        ('그룹4', '그룹4'),
        ('그룹5', '그룹5'),
    ]
    keyword_group = forms.ChoiceField(
        choices=KEYWORD_GROUP_CHOICES,
        label="키워드 그룹"
    )

    # 메인 키워드를 텍스트 필드로 대체
    main_keyword_text = forms.CharField(
        required=False,
        label="메인 키워드 (입력)",
        widget=forms.TextInput(attrs={'placeholder': '메인 키워드를 입력하세요 (선택사항)'})
    )

    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'main_keyword_text', 'keyword_group']
        labels = {
            'client': '클라이언트',
            'keyword': '키워드',
            'main_keyword_text': '메인 키워드',
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'keyword': forms.TextInput(attrs={'placeholder': '키워드를 입력하세요'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        main_keyword_text = cleaned_data.get('main_keyword_text')

        if main_keyword_text:
            try:
                matched_keyword = ShoppingKeyword.objects.get(
                    client=client,
                    keyword=main_keyword_text
                )
                self.instance.main_keyword = matched_keyword
            except ShoppingKeyword.DoesNotExist:
                raise forms.ValidationError(f"입력한 메인 키워드 '{main_keyword_text}'가 존재하지 않습니다.")
        else:
            self.instance.main_keyword = None

        return cleaned_data


class MainShoppingKeywordForm(forms.ModelForm):
    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'keyword_group']  # main_keyword 대신 keyword 사용
        labels = {
            'client': '클라이언트',
            'keyword': '메인 키워드 이름',  # 라벨은 메인 키워드 이름으로 표시
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'keyword': forms.TextInput(attrs={'placeholder': '메인 키워드 이름을 입력하세요'}),
            'keyword_group': forms.HiddenInput(),  # 숨겨진 필드로 처리
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        # 기본 키워드 그룹 값 설정
        self.fields['keyword_group'].initial = '기본'

    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']
        client = self.cleaned_data.get('client')

        if client and ShoppingKeyword.objects.filter(client=client, keyword=keyword).exists():
            raise forms.ValidationError(f"'{keyword}' 키워드는 이미 이 클라이언트에 존재합니다. 다른 이름을 사용해주세요.")
        return keyword

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 메인 키워드는 자기 자신을 참조하지 않도록 설정
        instance.main_keyword = None
        if commit:
            instance.save()
        return instance