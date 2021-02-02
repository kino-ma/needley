from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

import graphene

from .models import Profile, Article


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = ['username', 'profile', 'date_joined', 'last_login']
        fields = ['username', 'profile', 'date_joined', 'last_login']
        interfaces = (relay.Node, )

class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ['nickname', 'avator']
        fields = ['nickname', 'avator']
        interfaces = (relay.Node, )


class ArticleNode(DjangoObjectType):
    class Meta:
        model = Article
        filter_fields = {
            'author': ['exact'],
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
            'created_at': ['exact', 'lt', 'gt'],
            'updated_at': ['exact', 'lt', 'gt'],
        }
        fields = ['author', 'title', 'content', 'created_at', 'updated_at']
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    profile = relay.Node.Field(ProfileNode)

    article = relay.Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)


class CreateUser(relay.ClientIDMutation):
    class Input:
        user_name = graphene.String(required=True)
        user_email = graphene.String(required=True)
        user_password = graphene.String(required=True)
        user_nickname = graphene.String(required=True)
        user_avator = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        username = input.get('user_name')
        email = input.get('user_email')
        password = input.get('user_password')
        nickname = input.get('user_nickname')
        avator = input.get('user_avator')

        # name must be unique
        if User.objects.filter(username=username, email=email):
            raise Exception("User with that name already exests: %s" % username)

        user = User.objects.create_user(
            username=username, email=email, password=password)
        profile = Profile.objects.create(user=user, nickname=nickname, avator=avator)

        login(info.context, user)
        print(f'logged in as {user.profile}')

        return CreateUser(user=user)


class PostArticle(relay.ClientIDMutation):
    class Input:
        user_id = graphene.ID(required=True)
        article_title = graphene.String(required=True)
        article_content = graphene.String(required=True)

    article = graphene.Field(ArticleNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if not info.context.user.is_authenticated:
            raise Exception('Please login before posting your article.')

        user_id = input.get('user_id')
        title = input.get('article_title')
        content = input.get('article_content')

        user_pk = int(from_global_id(user_id)[1])
        user = get_object_or_404(User, pk=user_pk)

        article = Article.objects.create(
            author=user, title=title, content=content)

        return PostArticle(article=article)



class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    post_article = PostArticle.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
