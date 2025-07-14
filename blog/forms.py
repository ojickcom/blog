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
            'main_keyword': '메인 키워드 (선택 사항)', # 레이블 변경
            'keyword_group': '키워드 그룹',
        }
        widgets = {
            'keyword': forms.TextInput(attrs={'placeholder': '키워드를 입력하세요'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. 클라이언트 필드 제한: client_type이 'shopping'인 클라이언트만 표시
        self.fields['client'].queryset = Client.objects.filter(client_type='shopping').order_by('name')

        # 2. 메인 키워드 필드 설정 (선택 사항으로 만들기)
        # 이미 null=True, blank=True가 모델에 설정되어 있어 기본적으로 선택 사항입니다.
        # 드롭다운 옵션에 현재 클라이언트의 키워드만 보이게 하려면 필터링합니다.
        # 인스턴스가 있다면, 해당 인스턴스의 클라이언트에 속한 키워드만 메인 키워드 후보로 표시
        if self.instance and self.instance.pk: # 수정 모드일 때
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(
                client=self.instance.client
            ).exclude(pk=self.instance.pk).order_by('keyword') # 자기 자신은 메인 키워드가 될 수 없음
        else: # 생성 모드일 때 (클라이언트가 아직 선택되지 않았을 수 있으므로 모든 쇼핑 키워드를 보여줌)
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(
                client__client_type='shopping'
            ).order_by('keyword')
            
        # 선택된 클라이언트가 있을 경우, 메인 키워드 옵션을 해당 클라이언트에 한정
        # 초기 로드 시 클라이언트가 선택되지 않은 경우를 대비 (JS로 동적 업데이트 권장)
        client_id = self.initial.get('client') or self.data.get('client')
        if client_id:
            self.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(
                client_id=client_id,
                client__client_type='shopping' # 혹시 모르니 다시 한번 필터링
            ).exclude(pk=self.instance.pk if self.instance else None).order_by('keyword')

        # 메인 키워드 필드가 비어있을 수 있도록 빈 선택지 추가
        self.fields['main_keyword'].empty_label = "메인 키워드 없음 (선택 사항)"
        
        # 3. 키워드 그룹 필드는 ChoiceField로 이미 상단에 정의됨
        # 기본값을 '기본'이 아닌 첫 번째 옵션('그룹1')으로 설정하려면 initial 값을 줄 수 있습니다.
        # self.fields['keyword_group'].initial = '그룹1'