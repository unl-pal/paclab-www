import os
import shutil
import subprocess

from PIL import Image
from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import ListView, View

from website.forms import StaffUserForm

from .choices import *
from .decorators import email_required, email_verify_warning, ghtoken_required
from .forms import (
    BioProfileForm, EmailForm, FilterFormSet, ProfileForm, ProjectSelectionForm,
    TransformOptionForm, UserForm, UserFormLogin, UserFormRegister,
    UserPasswordForm)
from .mixins import EmailRequiredMixin
from .models import (
    Filter, FilterDetail, Paper, ProjectSelector, ProjectTransformer)
from .tokens import email_verify_token

class PapersView(ListView):
    template_name = 'website/papers.html'
    context_object_name = 'allPapers'
    paginate_by = 25
    queryset = Paper.objects.all()
    ordering = ['-date']

class PeopleView(ListView):
    template_name = 'website/people.html'
    context_object_name = 'allPeople'
    paginate_by = 10
    queryset = User.objects.exclude(profile__staffStatus=USER)
    ordering = ['profile__staffStatus', 'last_name']

class RegisterView(View):
    form_class = UserFormRegister
    template_name = 'website/user/register.html'
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form' : form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.privacy_agreement = form.cleaned_data['privacy_agreement']
            user.profile.terms_agreement = form.cleaned_data['terms_agreement']
            user.profile.age_confirmation = form.cleaned_data['age_confirmation']
            user.profile.save()
            login(request, user)
            send_email_verify(request, user, 'Verify your email with PAClab')
            messages.info(request, 'Please check and confirm your email to complete registration.')
            return redirect('website:index')
        return render(request, self.template_name, {'form' : form})

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and email_verify_token.check_token(user, token):
        user.profile.active_email = True
        user.profile.save()
        login(request, user)
    messages.info(request, 'If you followed a valid email verification link, your email is now verified.')
    return redirect('website:index')

class LoginView(View):
    form_class = UserFormLogin
    template_name = 'website/user/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form' : form, 'next' : request.GET.get('next')})

    def post(self, request):
        form = self.form_class(request.POST)
        next = request.POST.get('next')
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not user.profile.active_email:
                        return email_verify_warning(request)
                    if next:
                        return redirect(next)
                    return redirect('website:index')
        return render(request, self.template_name, {'form' : form, 'next' : next})

class SelectionListView(EmailRequiredMixin, ListView):
    template_name = 'website/selections/list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        return ProjectSelector.objects.filter(user=self.request.user).exclude(enabled=False).order_by('-created')

class TransformListView(EmailRequiredMixin, ListView):
    template_name = 'website/transforms/list.html'
    context_object_name = 'transformers'
    paginate_by = 20

    def get_queryset(self):
        return ProjectTransformer.objects.filter(user=self.request.user).exclude(enabled=False).order_by('-created')

def selection_detail(request, slug):
    try:
        model = ProjectSelector.objects.get(slug=slug)
    except:
        raise Http404
    if not model.enabled and not request.user.has_perm('website.view_disabled'):
        raise Http404
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid() and request.user == model.user or request.user.has_perm('website.view_projectselector'):
            send_list = form.cleaned_data['email'].split(',')
            to = set()
            for user in send_list:
                if '@' in user:
                    to.add(user)
                else:
                    name, username = user.split('(')
                    username = username.rstrip(')')
                    email = str(User.objects.get(username=username).email)
                    to.add(email)
            user = str(request.user.username)
            url = request.build_absolute_uri('/selection/' + slug+ '/')
            text_content = user + ' has shared a project selection with you on PAClab: ' + url
            html_content = get_template('website/selections/shared_email.html').render({'user' : user, 'url' : url})
            msg = EmailMultiAlternatives('PAClab Project Selection', text_content, request.user.email, list(to))
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, 'Email invitation(s) sent')
        else:
            messages.warning(request, 'Invalid form entry')
    form = EmailForm()
    values = FilterDetail.objects.filter(project_selector=model)
    return render(request, 'website/selections/detail.html', {'project' : model, 'form' : form, 'values' : values, 'is_done' : model.isDone(), 'cloned': model.project.exclude(host__isnull=True).exclude(path__isnull=True).count(), 'download_size' : download_size(model.slug)})

def transform_detail(request, slug):
    try:
        model = ProjectTransformer.objects.get(slug=slug)
    except:
        raise Http404
    if not model.enabled and not request.user.has_perm('website.view_disabled'):
        raise Http404
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid() and request.user == model.user or request.user.has_perm('website.view_projecttransformer'):
            send_list = form.cleaned_data['email'].split(',')
            to = set()
            for user in send_list:
                if '@' in user:
                    to.add(user)
                else:
                    name, username = user.split('(')
                    username = username.rstrip(')')
                    email = str(User.objects.get(username=username).email)
                    to.add(email)
            user = str(request.user.username)
            url = request.build_absolute_uri('/transform/' + slug + '/')
            text_content = user + ' has shared a project transform with you on PAClab: ' + url
            html_content = get_template('website/transforms/shared_email.html').render({'user' : user, 'url' : url})
            msg = EmailMultiAlternatives('PAClab Project Transform', text_content, request.user.email, list(to))
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, 'Email invitation(s) sent')
        else:
            messages.warning(request, 'Invalid form entry')
    form = EmailForm()
    done = not model.transformed_projects.exclude(host__isnull=False).exclude(path__isnull=False).exists()
    return render(request, 'website/transforms/detail.html', {'transformer' : model, 'form' : form, 'done': done, 'transformed': model.transformed_projects.exclude(host__isnull=True).exclude(path__isnull=True).count(), 'download_size' : download_size(model.slug)})

@email_required
def delete_selection(request, slug):
    try:
        model = ProjectSelector.objects.get(slug=slug)
    except:
        raise Http404
    if request.method == 'POST':
        if request.user == model.user or request.user.has_perm('website.delete_projectselector'):
            model.enabled = False
            model.save()
            messages.info(request, 'Project selection \'' + slug + '\' was deleted')
            return redirect('website:list_selections')
        else:
            messages.warning(request, 'You do not have access to delete this project selection')
    return render(request, 'website/delete.html', {'asset' : 'project selection', 'cancel' : reverse_lazy('website:selection_detail', args=(slug,))})

@email_required
def delete_transform(request, slug):
    try:
        model = ProjectTransformer.objects.get(slug=slug)
    except:
        raise Http404
    if request.method == 'POST':
        if request.user == model.user or request.user.has_perm('website.delete_projecttransformer'):
            model.enabled = False
            model.save()
            messages.info(request, 'Project transform was deleted')
            return redirect('website:list_transforms')
        else:
            messages.warning(request, 'You are not the owner of this transform and cannot delete it')
    return render(request, 'website/delete.html', {'asset' : 'project transform', 'cancel' : reverse_lazy('website:transform_detail', args=(slug,))})

def api_usernames(request):
    q = request.GET.get('term', '')
    results = []
    if len(q) > 2:
        for r in User.objects.filter(username__icontains=q).filter(is_active=True).filter(profile__active_email=True)[:10]:
            results.append(r.first_name + ' ' + r.last_name + ' (' + r.username + ')')
    return JsonResponse(results, safe=False)

def logoutView(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('website:index')

@login_required
def profile(request):
    if request.method == 'POST':
        if request.user.profile.hasBio():
            userForm = StaffUserForm(request.POST, instance=request.user)
            profileForm = BioProfileForm(request.POST, request.FILES, instance=request.user.profile)
        else:
            userForm = UserForm(request.POST, instance=request.user)
            profileForm = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if userForm.is_valid() and profileForm.is_valid():
            userForm.save()
            profileForm.save()
            if 'email' in userForm.changed_data:
                request.user.profile.active_email = False
                request.user.profile.save()
                send_email_verify(request, request.user, 'Verify your email with PAClab')

            if profileForm.cleaned_data['photo']:
                image = Image.open(request.user.profile.photo)

                try:
                    x = float(request.POST.get('crop_x', 0))
                    y = float(request.POST.get('crop_y', 0))
                    w = float(request.POST.get('crop_w', 0))
                    h = float(request.POST.get('crop_h', 0))
                    if x and y and w and h:
                        image = image.crop((x, y, w + x, h + y))
                except:
                    pass

                image = image.resize(settings.THUMBNAIL_SIZE, Image.LANCZOS)
                image.save(request.user.profile.photo.path)

            messages.success(request, 'Profile successfully updated')
            return redirect('website:edit_profile')
        else:
            messages.error(request, 'Invalid form entry')
    else:
        if request.user.profile.hasBio():
            userForm = StaffUserForm(instance=request.user)
            profileForm = BioProfileForm(instance=request.user.profile)
        else:
            userForm = UserForm(instance=request.user)
            profileForm = ProfileForm(instance=request.user.profile)
    return render(request, 'website/user/editprofile.html', {'userForm' : userForm, 'profileForm' : profileForm, 'min_width' : settings.THUMBNAIL_SIZE, 'min_height' : settings.THUMBNAIL_SIZE})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = UserPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated!')
            return redirect('website:index')
        messages.error(request, 'Invalid form entry')
    else:
        form = UserPasswordForm(request.user)
    return render(request, 'website/user/password_change.html', {'form' : form})

@email_required
@ghtoken_required
def create_selection(request):
    template_name = 'website/selections/create.html'
    if request.method == 'GET':
        p_form = ProjectSelectionForm(request.GET or None)
        formset = FilterFormSet(request.GET or None)
    elif request.method == 'POST':
        p_form = ProjectSelectionForm(request.POST)
        formset = FilterFormSet(request.POST)
        if p_form.is_valid() and formset.is_valid():
            selector = ProjectSelector()
            selector.user = request.user
            selector.input_dataset = p_form.cleaned_data['input_dataset']
            selector.save()
            for form in formset:
                pfilter = form.cleaned_data.get('pfilter')
                value = form.cleaned_data.get('value')
                if value and pfilter:
                    try:
                        connection = FilterDetail()
                        connection.project_selector = ProjectSelector.objects.all().last()
                        pk = form.cleaned_data.get('pfilter').id
                        connection.pfilter = Filter.objects.get(pk=pk)
                        connection.value = form.cleaned_data['value']
                        connection.save()
                    except:
                        pass
            messages.success(request, 'Project selection created successfully.')
            return redirect(reverse_lazy('website:selection_detail', args=(selector.slug,)))
        messages.error(request, 'Invalid form entry')
    return render(request, template_name, {
        'p_form' : p_form,
        'formset': formset,
    })

@ghtoken_required
def create_transform_selection(request, slug):
    try:
        selector = ProjectSelector.objects.get(slug=slug)
    except:
        raise Http404

    template_name = 'website/transforms/create.html'
    if request.method == 'GET':
        form = TransformOptionForm(request.GET or None)
    elif request.method == 'POST':
        form = TransformOptionForm(request.POST)
        if form.is_valid():
            options = form.save()
            create_transform = ProjectTransformer.objects.create(
                project_selector=selector,
                user=request.user,
                transform=options
            )
            messages.success(request, 'Project transform created successfully.')
            return redirect(reverse_lazy('website:transform_detail', args=(create_transform.slug,)))
        messages.error(request, 'Invalid form entry')
    return render(request, template_name, {
        'form' : form,
    })

@ghtoken_required
def create_transform_transform(request, slug):
    try:
        parent = ProjectTransformer.objects.get(slug=slug)
    except:
        raise Http404

    template_name = 'website/transforms/create.html'
    if request.method == 'GET':
        form = TransformOptionForm(request.GET or None)
    elif request.method == 'POST':
        form = TransformOptionForm(request.POST)
        if form.is_valid():
            options = form.save()
            create_transform = ProjectTransformer.objects.create(
                parent=parent,
                user=request.user,
                transform=options
            )
            messages.success(request, 'Project transform created successfully.')
            return redirect(reverse_lazy('website:transform_detail', args=(create_transform.slug,)))
        messages.error(request, 'Invalid form entry')
    return render(request, template_name, {
        'form' : form,
    })

def api_filter_detail(request):
    val = int(request.GET.get('id', 0))
    try:
        pfilter = Filter.objects.filter(enabled=True).get(pk=val)
    except:
        raise Http404
    return JsonResponse({
        'id' : val,
        'backend' : pfilter.associated_backend.name,
        'name' : pfilter.name,
        'val_type' : pfilter.val_type,
        'default' : pfilter.default_val,
        'help_text' : pfilter.help_text,
        })

def verify_email_link(request):
    return send_email_verify(request, request.user, 'Reconfirm email address')

def send_email_verify(request, user, title):
    current_site = get_current_site(request)
    message = render_to_string('website/user/verification_email.html', {
        'user' : user,
        'domain' : current_site.domain,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : email_verify_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(title, message, to=[to_email])
    email.send()
    messages.info(request, "If an account exists with the email you entered, we've emailed you a link for verifying the email address. You should receive the email shortly. If you don't receive an email, check your spam/junk folder and please make sure your email address is entered correctly in your profile.")
    return redirect('website:index')

def download_size(slug):
    download_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    zipfile_path = os.path.join(download_path, slug + '.zip')
    tmpdir = os.path.join(download_path, slug + '.tmp')

    if not os.path.exists(zipfile_path):
        if os.path.exists(tmpdir):
            return 0
        return -1
    return os.stat(zipfile_path).st_size

def download_selection(request, slug):
    download_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    download_filename = slug + '.zip'
    zipfile_path = os.path.join(download_path, download_filename)
    tmpdir = os.path.join(download_path, slug + '.tmp')

    if not os.path.exists(zipfile_path):
        if os.path.exists(tmpdir):
            return redirect(reverse_lazy('website:selection_detail', args=(slug,)))

        paths = {}

        try:
            for project in ProjectSelector.objects.get(slug=slug).project.exclude(path__isnull=True):
                transformed_project = project.transformedproject_set.exclude(path__isnull=True).first()
                if transformed_project:
                    if not transformed_project.host in paths:
                        paths[transformed_project.host] = []
                    paths[transformed_project.host].append(transformed_project.path)

            if not paths:
                raise RuntimeError('empty benchmark')
        except:
            raise Http404

        if not os.path.exists(download_path):
            os.mkdir(download_path, 0o755)
        os.mkdir(tmpdir, 0o755)

        transformed_path = config('TRANSFORMED_PATH')

        for host in paths:
            s = ""
            for path in paths[host]:
                s = s + path + '\n'
            p = subprocess.Popen(['zip', '-r', '-g', '-@', '-b', tmpdir, zipfile_path], cwd=os.path.join(transformed_path, host), stdin=subprocess.PIPE)
            p.communicate(input=str.encode(s))
            p.stdin.close()
            p.wait()

        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    return redirect(settings.MEDIA_URL + '/downloads/' + download_filename)

def download_transform(request, slug):
    download_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    download_filename = slug + '.zip'
    zipfile_path = os.path.join(download_path, download_filename)
    tmpdir = os.path.join(download_path, slug + '.tmp')

    if not os.path.exists(zipfile_path):
        if os.path.exists(tmpdir):
            return redirect(reverse_lazy('website:transform_detail', args=(slug,)))

        paths = {}

        try:
            for project in ProjectSelector.objects.get(slug=slug).project.exclude(path__isnull=True):
                transformed_project = project.transformedproject_set.exclude(path__isnull=True).first()
                if transformed_project:
                    if not transformed_project.host in paths:
                        paths[transformed_project.host] = []
                    paths[transformed_project.host].append(transformed_project.path)

            if not paths:
                raise RuntimeError('empty benchmark')
        except:
            raise Http404

        if not os.path.exists(download_path):
            os.mkdir(download_path, 0o755)
        os.mkdir(tmpdir, 0o755)

        transformed_path = config('TRANSFORMED_PATH')

        for host in paths:
            s = ""
            for path in paths[host]:
                s = s + path + '\n'
            p = subprocess.Popen(['zip', '-r', '-g', '-@', '-b', tmpdir, zipfile_path], cwd=os.path.join(transformed_path, host), stdin=subprocess.PIPE)
            p.communicate(input=str.encode(s))
            p.stdin.close()
            p.wait()

        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    return redirect(settings.MEDIA_URL + '/downloads/' + download_filename)
