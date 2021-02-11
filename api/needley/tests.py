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
    user_global_id = to_global_id("UserNode", user.pk)
    query = f'''
    {{
        user(id: "{user_global_id}") {{
            username
            profile {{
                nickname
                avator
            }}
        }}
    }}
    '''
    result = user_result_from(user)

    return {
        'query': query,
        'expect': result
    }


def user_result_from(user):
    if type(user).__name__ == "UserData":
        user = user.as_user()
    return {
        'data': {
            'user': {
                'username': user.username,
                'profile': {
                    'nickname': user.profile.nickname,
                    'avator': user.profile.avator,
                }
            }
        }
    }


def all_users_query(query_filter=None, search_filter=None):
    filter = ''
    if query_filter:
        filter = '(' + \
            ', '.join([k + f':"{v}"' for (k, v) in query_filter.items()]) + ')'

    if search_filter:
        all_users = User.objects.filter(**search_filter)
    else:
        all_users = User.objects.all()

    query = f'''
        {{
            allUsers{filter} {{
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
                        'node': user_result_from(user)['data']['user']
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
        # create 3 users before testing
        for count in range(3):
            created = get_mock_user()
        data = all_users_query()
        query = data['query']
        expect = data['expect']
        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_username(self):
        user = None
        for count in range(2):
            user = get_mock_user()

        query_filter = {'username': user.username}
        data = all_users_query(query_filter=query_filter,
                               search_filter=query_filter)
        query = data['query']
        expect = data['expect']
        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_nickname(self):
        user = None
        for count in range(2):
            user = get_mock_user()

        filter_word = user.profile.nickname[1:-1]
        query_filter = {'profile_Nickname_Icontains': filter_word}
        search_filter = {'profile__nickname__icontains': filter_word}
        data = all_users_query(query_filter=query_filter,
                               search_filter=search_filter)
        query = data['query']
        expect = data['expect']
        result = post_query(query)

        self.assertEqual(result, expect)

    def test_an_user(self):
        user = get_mock_user()
        data = user_query_and_result(user)
        query = data['query']
        expect = data['expect']
        result = post_query(query)

        self.assertEqual(result, expect)

    def test_me(self):
        user = get_mock_user()
        query = '''
        {
            me {
                user {
                    username
                }
                ok
            }
        }
        '''

        expect = {
            'data': {
                'me': {
                    'user': {
                        'username': user.username
                    },
                    'ok': True,
                }
            }
        }

        result = post_query(query, login_as=user)

        self.assertEqual(result, expect)


def create_user_mutation(name, email, password, nickname, avator=None):
    mutation = f'''
        mutation {{
            createUser(input: {{
                username:"{name}"
                email:"{email}"
                password:"{password}"
                nickname:"{nickname}"
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

    def as_user(self):
        # get_or_create returns Tuple (obj, created)
        user = User.objects.get_or_create(
            username=self.username, email=self.email, password=self.password)[0]
        Profile.objects.get_or_create(
            user=user, nickname=self.username, avator=self.avator)
        return user


def get_mock_user(data_only=False):
    idx = User.objects.count()
    username = "test" + str(idx)
    email = username + "@example.com"
    password = "password"
    nickname = username + " (nick)"

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


def post_article_mutation(title, content):
    mutation = f'''
        mutation {{
            postArticle(input: {{
                title:"{title}",
                content:"{content}",
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
        title = "fuga"
        content = "fuga fuga content"
        data = post_article_mutation(title, content)
        mutation = data['mutation']
        expect = data['expect']

        result = post_query(mutation, login_as=True)

        self.assertEqual(result, expect)
