from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

import graphene

from .models import User, Article


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = ['name', 'nickname', 'avator',
                         'created_at', 'updated_at']
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
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    article = relay.Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)


class CreateUser(relay.ClientIDMutation):
    class Input:
        user_name = graphene.String(required=True)
        user_nickname = graphene.String(required=True)
        user_avator = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        name = input.get('user_name')
        nickname = input.get('user_nickname')
        avator = input.get('user_avator')

        # name must be unique
        if User.lookup_name(name):
            raise Exception("User with that name already exests: %s" % name)

        if not name or not nickname:
            raise Exception(
                "`createuser` must have both `name` and `nickname` field.")

        user = User.objects.create(name=name, nickname=nickname, avator=avator)

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
