import json
from dataclasses import dataclass

from django.test import Client, TestCase
from graphene.test import Client as GraphQLClient
from graphql_relay import to_global_id

from .models import User, Article, Profile
from .schema import schema, UserNode


def post_query(query, login_as=None):
    client = Client()
    if login_as is True:
        user = get_mock_user()
        client.force_login(user)
    elif login_as:
        client.force_login(login_as)

    response = client.post('/graphql', {'query': query})
    parsed = json.loads(response.content)
    return parsed


def user_query_and_result(user):
    user_global_id = to_global_id(User, user.pk)
    query = f'''
    {{
        user(id: {user_global_id}) {{
            username
            profile {{
                nickname
                avator
            }}
        }}
    }}
    '''
    result = user_result_from(user)

    return (query, result)


def user_result_from(user):
    if type(user).__name__ == "UserData":
        user = user.as_user()
    return {
        'user': {
            'username': user.username,
            'profile': {
                'nickname': user.profile.nickname,
                'avator': user.profile.avator,
            }
        }
    }


def all_users_query(**filter):
    filter_query = ''
    if filter:
        filter_query = '(' + \
            ', '.join([k + f':"{v}"' for (k, v) in filter.items()]) + ')'

    all_users = User.objects.all(**filter)

    query = f'''
        {{
            allUsers{filter_query} {{
                edges {{
                    node {{
                        username
                        profile {{
                            nickname
                            avator
                        }}
                    }}
                }}
            }}
        }}
    '''

    expect = {
        'data': {
            'allUsers': {
                'edges': [
                    {
                        'node': user_result_from(user)['user']
                    }
                    for user in all_users
                ]
            }
        }
    }

    return {
        'query': query,
        'expect': expect
    }


class GetUserTests(TestCase):
    def test_all_users(self):
        self.maxDiff = None
        # create 3 users before testing
        for count in range(3):
            get_mock_user()
        data = all_users_query()
        query = data['query']
        expect = data['expect']
        result = post_query(query)

        self.assertEqual(result, expect)


def create_user_mutation(name, email, password, nickname, avator=None):
    mutation = f'''
        mutation {{
            createUser(input: {{
                userName:"{name}"
                userEmail:"{email}"
                userPassword:"{password}"
                userNickname:"{nickname}"
                { 'userAvator:"' + avator + '"' if avator else "" }
            }}) {{
                user {{
                    username
                    profile {{
                        nickname
                        avator
                    }}
                }}
            }}
        }}
        '''

    expect = {
        'data': {
            'createUser': {
                'user': {
                    'username': name,
                    'profile': {
                        'nickname': nickname,
                        'avator': avator,
                    }
                }
            }
        }
    }

    return {
        'mutation': mutation,
        'expect': expect
    }

@dataclass
class UserData:
    username: str
    email: str
    password: str
    nickname: str = "hoge-nick"
    avator: str = None
    idx = 0

    def as_user(self):
        # get_or_create returns Tuple (obj, created)
        user = User.objects.get_or_create(
            username=self.username, email=self.email, password=self.password)[0]
        Profile.objects.get_or_create(
            user=user, nickname=self.username, avator=self.avator)
        return user

def get_mock_user(data_only=False):
    username = "test" + str(UserData.idx)
    email = username + "@example.com"
    password = "password"
    nickname = username + " (nick)"
    UserData.idx += 1

    user_data = UserData(username=username, email=email, password=password)

    if data_only:
        return user_data
    else:
        return user_data.as_user()


class CreateUserTests(TestCase):
    def test_create_user(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avator=u.avator)
        mutation = data['mutation']
        expect = data['expect']
        result = post_query(mutation)

        self.assertEqual(result, expect)

    def test_create_user_without_avator(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avator=None)
        mutation = data['mutation']
        expect = data['expect']
        result = post_query(mutation)

        self.assertEqual(result, expect)


def post_article_mutation(user_id, title, content):
    mutation = f'''
        mutation {{
            postArticle(input: {{
                userId:"{user_id}",
                articleTitle:"{title}",
                articleContent:"{content}",
            }}) {{
                article {{
                    title
                    content
                }}
            }}
        }}
        '''
    expect = {
        'data': {
            'postArticle': {
                'article': {
                    'title': title,
                    'content': content,
                }
            }
        }
    }

    return {
        'mutation': mutation,
        'expect': expect
    }




class PostArticleTests(TestCase):
    def test_post_article(self):
        user = get_mock_user()
        user_id = to_global_id(UserNode._meta.name, user.pk)

        title = "fuga"
        content = "fuga fuga content"
        data = post_article_mutation(user_id, title, content)
        mutation = data['mutation']
        expect = data['expect']

        result = post_query(mutation, login_as=True)

        self.assertEqual(result, expect)
