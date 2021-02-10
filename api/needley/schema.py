from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectTypeOptions
from graphql_relay import from_global_id

import graphene

from .models import Profile, Article


class UserMeta:
    model = User
    filter_fields = ['username', 'profile', 'date_joined', 'last_login']
    fields = ['username', 'profile', 'date_joined', 'last_login']
    interfaces = (relay.Node, )


class UserNode(DjangoObjectType):
    class Meta(UserMeta):
        pass


class MeNode(UserNode):
    class Meta(UserMeta):
        filter_fields = []
        fields = UserMeta.fields + ['email']
        interfaces = ()

    # @classmethod
    def resolve_me(parent, info):
        print("get_node")
        print("me:", info.context.user)
        return UserNode.get_node(info, info.context.user.id)


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
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)
    me = graphene.Field(UserNode)

    profile = relay.Node.Field(ProfileNode)

    article = relay.Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)

    def resolve_me(parent, info):
        return UserNode.get_node(info, info.context.user.id)


class CreateUser(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        nickname = graphene.String(required=True)
        avator = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        username = input.get('username')
        email = input.get('email')
        password = input.get('password')
        nickname = input.get('nickname')
        avator = input.get('avator')

        # name must be unique
        if User.objects.filter(username=username, email=email):
            raise Exception(
                "User with that name already exests: %s" % username)

        user = User.objects.create_user(
            username=username, email=email, password=password)
        profile = Profile.objects.create(
            user=user, nickname=nickname, avator=avator)

        login(info.context, user)
        print(f'logged in as {user.profile}')

        return CreateUser(user=user)


class Login(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    me = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = authenticate(info.context, username=input.get(
            'username'), password=input.get('password'))
        if user is not None:
            login(info.context, user)
            print('logged in as %s' % user.username)
            return Login(me=user)
        else:
            raise Exception('invalid credentials')


class PostArticle(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    article = graphene.Field(ArticleNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if not info.context.user.is_authenticated:
            raise Exception('Please login before posting your article.')

        title = input.get('title')
        content = input.get('content')
        user = info.context.user

        article = Article.objects.create(
            author=user, title=title, content=content)

        return PostArticle(article=article)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = Login.Field()
    post_article = PostArticle.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
