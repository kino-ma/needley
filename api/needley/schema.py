from icecream import ic
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user, login, authenticate, get_user_model
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectTypeOptions
from graphql_relay import from_global_id

import graphene

from .models import Article

User = get_user_model()


class UserMeta:
    model = User
    filter_fields = {
        'username': ['exact', 'icontains'],
        'nickname': ['exact', 'icontains'],
    }
    fields = ['username', 'nickname', 'avatar', 'date_joined', 'last_login']
    interfaces = (relay.Node, )


class UserNode(DjangoObjectType):
    class Meta(UserMeta):
        pass


class MeUserNode(UserNode):
    class Meta(UserMeta):
        filter_fields = []
        fields = UserMeta.fields + ['email']
        interfaces = ()


class Me(graphene.ObjectType):
    user = graphene.Field(UserNode)
    ok = graphene.Boolean()

    def resolve_user(parent, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('You are not authorized.')
        return MeUserNode.get_node(info, info.context.user.id)

    def resolve_ok(parent, info):
        return info.context.user.is_authenticated



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
    me = graphene.Field(Me)

    article = relay.Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)

    def resolve_me(parent, info):
        return Me()


class CreateUser(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        nickname = graphene.String(required=True)
        avatar = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        username = input.get('username')
        email = input.get('email')
        password = input.get('password')
        nickname = input.get('nickname')
        avatar = input.get('avatar')

        login_user = User.objects.create_user(
            username=username, email=email, password=password, nickname=nickname, avatar=avatar)

        login(info.context, login_user)
        ic(login_user)

        return CreateUser(user=login_user)


class Login(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    me = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        login_user = authenticate(info.context, username=input.get(
            'username'), password=input.get('password'))
        if login_user is not None:
            login(info.context, login_user)
            ic(login_user)
            return Login(login_user)
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
