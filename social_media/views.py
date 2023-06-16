from itertools import chain
import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from social_media.models import Profile, Post, LikePost, FollowersCount


# Create your views here.
def welcome(request):
    return render(request, 'welcome.html')


@login_required(login_url='/signin')
def home(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Faccio in modo che l'utente possa vedere i post solo delle persone che segue
    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for user in user_following:
        user_following_list.append(user.user)

    for username in user_following_list:
        feed_list = Post.objects.filter(user=username)
        feed.append(feed_list) # ottengo così un queryset

    user_feed_list = list(chain(*feed))
    user_feed_list.sort(key=lambda x: x.id) # ordino in base all'id degli user


    # Faccio vedere alcuni suggerimenti per l'utente
    all_users = User.objects.all()
    user_following_all = [] # questa sarà la lista degli utenti che già segue

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestion_list = [
        x for x in list(all_users) if (x not in list(user_following_all))
    ]
    # mi devo ricordare di togliere me stesso
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [
        x for x in list(new_suggestion_list) if (x not in list(current_user))
    ]


    # Voglio quindi stamparne 3 max e ogni volta in modo random
    random.shuffle(final_suggestion_list)

    # Ne voglio ricavare il profilo in modo da poi stampare le altre info (simile al search)
    username_profile = []
    username_profile_list = []
    for user in final_suggestion_list:
        username_profile.append(user.id)
    for id in username_profile:
        profile_list = Profile.objects.filter(id_user=id)
        username_profile_list.append(profile_list)

    suggestion_username_profile_list = list(chain(*username_profile_list))[:3]

    # Per ogni utente guardo a quali post ha messo like
    user_likes = LikePost.objects.filter(username=user_object)
    user_likes_id = []
    for user_like in user_likes:
        user_likes_id.append(user_like.post_id.id)

    context = {
        'user_profile': user_profile,
        'posts': user_feed_list,
        'suggestion_username_profile_list': suggestion_username_profile_list,
        'user_likes_id': user_likes_id,
    }
    return render(request, 'home.html', context)


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']  # vado a ricercare il name dell'imput che combacia e prendo l'info
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already taken')
                return redirect('/')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken')
                return redirect('/')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # Se tutto ha avuto successo va fatto il login dell'user portandolo a impostare gli altri campi
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Quindi creiamo il profilo dell'utente
                user_model = User.objects.get(username=username)  # questo è un oggetto user con username quello passato
                new_profile = Profile.objects.create(user=user_model,
                                                     id_user=user_model.id)  # il resto lo può aggiungere succesivamente
                new_profile.save()
                return redirect('/settings')
        else:
            messages.info(request, 'Password not matching')
            return redirect('/signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,
                                 password=password)  # se l'utente nel db ritorna qualcosa diverso da none

        if user is not None:
            auth.login(request, user)
            return redirect('home')  # torno all'home page
        else:
            messages.info(request, 'Credentials not valid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='/signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='/signin')
def settings(request):
    # vista per modificare le impostazione del profilo
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # controllo che l'utente abbia submitted un immagine
        if request.FILES.get('image') is None:
            image = user_profile.profile_img  # se non presente ricarico quella presente
            bio = request.POST['bio']
            location = request.POST['location']

        else:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('profile', user_name=user_profile)
    else:
        return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='/signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')  # nell'html il campo si chiama image_upload
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('profile', user_name=user)
    else:
        return redirect('home')


@login_required(login_url='/signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post, username=username).first()  # in modo che te ne dia solo uno

    if like_filter == None:
        # in questo caso l'utente non ha messo like al post
        new_like = LikePost.objects.create(post_id=post, username=username, liked=True)  # e lo aggiungo
        new_like.save()
        # voglio quindi aumentare il numero dei like
        post.number_of_likes += 1
        post.save()
        return redirect('home')
    else:
        # in questo caso l'utente lo ha già messo e quindi lo toglie
        like_filter.delete()
        post.number_of_likes -= 1
        post.save()

        return redirect('home')


@login_required(login_url='/signin')
def profile(request, user_name):
    user_object = User.objects.get(username=user_name)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_name)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = user_name

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=user_name))
    user_following = len(FollowersCount.objects.filter(follower=user_name))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['username']

        # Inizialmente controllo se l'utente segue già l'user che vuole seguire
        if FollowersCount.objects.filter(follower=follower,
                                         user=user).first():  # si usa filter per non avere problemi di non esistenza
            # a questo punto so già che esiste e quindi tolgo il follow
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('home')
        else:
            # qui invece lo aggiungo
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('home')

    else:
        return redirect('home')


@login_required(login_url='/signin')
def search(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_objects = User.objects.filter(username__icontains=username) # ottiene una lista di elementi che contengono quella parola

        username_profiles = []
        username_profile_list = []

        for user in username_objects:
            username_profiles.append(user.id)

        for id in username_profiles:
            profile = Profile.objects.filter(id_user=id)
            username_profile_list.append(profile)

        username_profiles_list = list(chain(*username_profile_list))

    context = {
        'username': username,
        'user_profile': user_profile,
        'username_profiles_list': username_profiles_list,
    }
    return render(request, 'search.html', context)


@login_required(login_url='/signin')
def view_followers(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user = user_profile.user

    followers = FollowersCount.objects.filter(user=user)
    follower_profile_list = []
    follower_profiles_list = []
    for follower in followers:
        user_name = User.objects.get(username=follower.follower)
        profile = Profile.objects.filter(user=user_name)
        follower_profile_list.append(profile)

        follower_profiles_list = list(chain(*follower_profile_list))

    context = {
        'username': user,
        'user_profile': user_profile,
        'follower_profiles_list': follower_profiles_list,
    }
    return render(request, 'followers.html', context)


@login_required(login_url='/signin')
def view_following(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user = user_profile.user

    following = FollowersCount.objects.filter(follower=user)
    following_profile_list = []
    following_profiles_list = []
    for follower in following:
        user_name = User.objects.get(username=follower.user)
        profile = Profile.objects.filter(user=user_name)
        following_profile_list.append(profile)

        following_profiles_list = list(chain(*following_profile_list))

    context = {
        'username': user,
        'user_profile': user_profile,
        'following_profiles_list': following_profiles_list,
    }
    return render(request, 'following.html', context)


