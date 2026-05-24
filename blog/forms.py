from django import forms

from .models import Blog, Client, KeywordGroup, ShoppingKeyword


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["client", "b_title", "title", "content"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "b_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "B_제목을 입력하세요 (선택 사항)",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "블로그 제목을 입력하세요 (비워두면 자동 생성)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "400자 이상의 내용을 입력하세요",
                }
            ),
        }
        labels = {
            "client": "클라이언트",
            "b_title": "B_제목",
            "title": "제목",
            "content": "내용",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.all().order_by("name")
        self.fields["client"].empty_label = "--- 클라이언트를 선택하세요 ---"

    def clean_content(self):
        content = self.cleaned_data["content"]
        if len(content) < 400:
            raise forms.ValidationError("내용은 400자 이상이어야 합니다.")
        return content


class MainKeywordInitialAddForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="키워드 그룹",
    )

    class Meta:
        model = ShoppingKeyword
        fields = ["client", "keyword", "groups"]
        labels = {
            "client": "클라이언트",
            "keyword": "메인 키워드 이름",
            "groups": "키워드 그룹",
        }
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "keyword": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "새로운 메인 키워드 이름을 입력하세요",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.all().order_by("name")
        self.fields["client"].empty_label = "클라이언트를 선택하세요"

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        keyword = (cleaned_data.get("keyword") or "").strip()

        if client and keyword:
            exists = ShoppingKeyword.objects.filter(
                client=client,
                keyword=keyword,
                main_keyword__isnull=True,
            ).exists()
            if exists:
                raise forms.ValidationError("같은 클라이언트에 동일한 메인 키워드가 이미 존재합니다.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.main_keyword = None
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class MainKeywordNameUpdateForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="키워드 그룹",
    )

    class Meta:
        model = ShoppingKeyword
        fields = ["keyword", "groups"]
        labels = {
            "keyword": "메인 키워드 이름",
            "groups": "키워드 그룹",
        }
        widgets = {
            "keyword": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "메인 키워드 이름을 입력하세요",
                }
            ),
        }

    def clean_keyword(self):
        keyword = (self.cleaned_data["keyword"] or "").strip()
        client = self.instance.client
        if client:
            exists = ShoppingKeyword.objects.filter(
                client=client,
                keyword=keyword,
            ).exclude(pk=self.instance.pk).exists()
            if exists:
                raise forms.ValidationError("같은 클라이언트에 동일한 키워드가 이미 존재합니다.")
        return keyword

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SubKeywordAddForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=KeywordGroup.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="키워드 그룹 (선택)",
    )

    class Meta:
        model = ShoppingKeyword
        fields = ["client", "main_keyword", "keyword", "groups"]
        labels = {
            "client": "클라이언트",
            "main_keyword": "상위 메인 키워드",
            "keyword": "서브 키워드",
            "groups": "키워드 그룹",
        }
        widgets = {
            "client": forms.Select(attrs={"class": "form-control"}),
            "main_keyword": forms.Select(attrs={"class": "form-control"}),
            "keyword": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "서브 키워드를 입력하세요",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.all().order_by("name")
        self.fields["client"].empty_label = "--- 클라이언트를 선택하세요 ---"
        self.fields["main_keyword"].queryset = (
            ShoppingKeyword.objects.filter(main_keyword__isnull=True)
            .exclude(keyword="")
            .select_related("client")
            .order_by("client__name", "keyword")
        )
        self.fields["main_keyword"].empty_label = "--- 상위 메인 키워드를 선택하세요 ---"

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        main_keyword = cleaned_data.get("main_keyword")
        keyword = (cleaned_data.get("keyword") or "").strip()

        if not main_keyword:
            raise forms.ValidationError("상위 메인 키워드를 반드시 선택해야 합니다.")

        if client and main_keyword and main_keyword.client_id != client.id:
            raise forms.ValidationError("선택한 클라이언트와 상위 메인 키워드의 클라이언트가 일치해야 합니다.")

        if client and keyword:
            exists = ShoppingKeyword.objects.filter(client=client, keyword=keyword).exists()
            if exists:
                raise forms.ValidationError("같은 클라이언트에 동일한 키워드가 이미 존재합니다.")

        return cleaned_data
