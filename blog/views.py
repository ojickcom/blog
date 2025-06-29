from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Client
from .forms import BlogForm

def blog_write(request):
    """블로그 작성 페이지"""
    print("DEBUG: blog_write view called!") # 이 줄 추가
    if request.method == 'POST':
        print("DEBUG: Request method is POST.") # 이 줄 추가
        form = BlogForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid.") # 이 줄 추가
            blog = form.save()
            print(f"DEBUG: Blog saved with ID: {blog.pk}") # 이 줄 추가
            return redirect('blog_list')
        else:
            print(f"DEBUG: Form is NOT valid. Errors: {form.errors}") # 이 줄 추가
    else:
        print("DEBUG: Request method is GET. Displaying empty form.") # 이 줄 추가
        form = BlogForm()
    
    return render(request, 'blog/write.html', {'form': form})