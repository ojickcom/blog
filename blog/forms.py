from django import forms
from .models import Blog, Client, ShoppingKeyword

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
            'keyword': forms.TextInput(attrs={'placeholder': '키워드를 입력하세요'}),
            'main_keyword': forms.TextInput(attrs={'placeholder': '메인 키워드를 입력하세요 (선택사항)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')


class MainShoppingKeywordForm(forms.ModelForm):
    class Meta:
        model = ShoppingKeyword
        fields = ['client', 'keyword', 'keyword_group']
        labels = {
            'client': '클라이언트',
            'keyword': '메인 키워드 이름',
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'keyword': forms.TextInput(attrs={'placeholder': '메인 키워드 이름을 입력하세요'}),
            'keyword_group': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')
        self.fields['keyword_group'].initial = '기본'

    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']
        client = self.cleaned_data.get('client')

        if client and ShoppingKeyword.objects.filter(client=client, keyword=keyword).exists():
            raise forms.ValidationError(f"'{keyword}' 키워드는 이미 이 클라이언트에 존재합니다. 다른 이름을 사용해주세요.")
        return keyword

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 메인 키워드는 main_keyword 필드를 비워둠 (또는 None)
        instance.main_keyword = None
        if commit:
            instance.save()
        return instance