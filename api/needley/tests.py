import json
import datetime
from dataclasses import dataclass
from unittest.signals import removeResult

from django.test import Client, TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
import graphene
from graphene.test import Client as GraphQLClient
from graphql_relay import to_global_id

from .models import Article
from .schema import schema, UserNode

User = get_user_model()


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
            nickname
            avatar
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
                'nickname': user.nickname,
                'avatar': user.avatar,
            }
        }
    }


def all_users_query(query_filter=None, search_filter=None):
    filter = ''
    if query_filter:
        filter = '(' + \
            ', '.join([k + f':{json.dumps(v)}' for (k, v)
                       in query_filter.items()]) + ')'

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
                        nickname
                        avatar
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

    def test_filter_user_username(self):
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

    def test_filter_user_nickname(self):
        user = None
        for count in range(3):
            user = get_mock_user()

        filter_word = user.nickname[1:-1]
        query_filter = {'nickname_Icontains': filter_word}
        search_filter = {'nickname__icontains': filter_word}
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


def create_user_mutation(name, email, password, nickname, avatar=None):
    mutation = f'''
        mutation {{
            createUser(input: {{
                username:"{name}"
                email:"{email}"
                password:"{password}"
                nickname:"{nickname}"
                { 'userAvator:"' + avatar + '"' if avatar else "" }
            }}) {{
                user {{
                    username
                    nickname
                    avatar
                }}
            }}
        }}
        '''

    expect = {
        'data': {
            'createUser': {
                'user': {
                    'username': name,
                    'nickname': nickname,
                    'avatar': avatar,
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
    avatar: str = None

    def as_user(self):
        # get_or_create returns Tuple (obj, created)
        user = User.objects.get_or_create(
            username=self.username, email=self.email, password=self.password, nickname=self.username)[0]
        return user


def get_mock_user(data_only=False):
    idx = User.objects.count()
    username = "test" + str(idx)
    email = username + "@example.com"
    password = "password"

    user_data = UserData(username=username, email=email, password=password)

    if data_only:
        return user_data
    else:
        return user_data.as_user()


class CreateUserTests(TestCase):
    def test_create_user(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avatar=u.avatar)
        mutation = data['mutation']
        expect = data['expect']
        result = post_query(mutation)

        self.assertEqual(result, expect)

    def test_create_user_without_avatar(self):
        u = get_mock_user(data_only=True)

        data = create_user_mutation(
            u.username, u.email, u.password, u.nickname, avatar=None)
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


def article_result_from(article):
    return {
        'data': {
            'article': {
                'title': article.title,
                'content': article.content
            }
        }
    }


def all_articles_query(query_filter=None, search_filter=None):
    filter = ''
    if query_filter:
        filter = '(' + \
            ', '.join([k + f':{json.dumps(v)}' for (k, v)
                       in query_filter.items()]) + ')'

    if search_filter:
        all_articles = Article.objects.filter(**search_filter)
    else:
        all_articles = Article.objects.all()

    query = f'''
        {{
            allArticles{filter} {{
                edges {{
                    node {{
                        title
                        content
                    }}
                }}
            }}
        }}
    '''

    expect = {
        'data': {
            'allArticles': {
                'edges': [
                    {
                        'node': article_result_from(article)['data']['article']
                    }
                    for article in all_articles
                ]
            }
        }
    }

    return {
        'query': query,
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

    def test_all_articles(self):
        author = get_mock_user()
        titles = ['test title 1', 'test title 2', 'title 3']
        contents = ['test content 1', 'test content 2', 'content 3']

        for (title, content) in zip(titles, contents):
            Article.objects.create(title=title, content=content, author=author)

        data = all_articles_query()
        query = data['query']
        expect = data['expect']

        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_articles_title(self):
        author = get_mock_user()
        titles = ['test title 1', 'test title 2', 'title 3']
        contents = ['test content 1', 'content 2', 'content 3']

        for (title, content) in zip(titles, contents):
            Article.objects.create(title=title, content=content, author=author)

        filter_word = 'test'
        query_filter = {'title_Icontains': filter_word}
        search_filter = {'title__icontains': filter_word}

        data = all_articles_query(
            query_filter=query_filter, search_filter=search_filter)
        query = data['query']
        expect = data['expect']

        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_articles_content(self):
        author = get_mock_user()
        titles = ['test title 1', 'test title 2', 'title 3']
        contents = ['test content 1', 'content 2', 'content 3']

        for (title, content) in zip(titles, contents):
            Article.objects.create(title=title, content=content, author=author)

        filter_word = 'test'
        query_filter = {'content_Icontains': filter_word}
        search_filter = {'content__icontains': filter_word}

        data = all_articles_query(
            query_filter=query_filter, search_filter=search_filter)
        query = data['query']
        expect = data['expect']

        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_articles_created_at(self):
        author = get_mock_user()
        titles = ['test title 1', 'test title 2', 'title 3']
        contents = ['test content 1', 'content 2', 'content 3']
        today = timezone.now()
        yesterday = timezone.now() - datetime.timedelta(days=1)
        dates = [today, today, yesterday]

        for (title, content, date) in zip(titles, contents, dates):
            Article.objects.create(
                title=title, content=content, author=author, updated_at=date)

        filter_date = graphene.DateTime.serialize(yesterday)
        query_filter = {'createdAt_Lt': filter_date}
        search_filter = {'created_at__lt': filter_date}

        data = all_articles_query(
            query_filter=query_filter, search_filter=search_filter)
        query = data['query']
        expect = data['expect']

        result = post_query(query)

        self.assertEqual(result, expect)

    def test_filter_articles_updated_at(self):
        author = get_mock_user()
        titles = ['test title 1', 'test title 2', 'title 3']
        contents = ['test content 1', 'content 2', 'content 3']
        today = timezone.now()
        yesterday = timezone.now() - datetime.timedelta(days=1)
        dates = [today, today, yesterday]

        for (title, content, date) in zip(titles, contents, dates):
            Article.objects.create(
                title=title, content=content, author=author, updated_at=date)

        filter_date = graphene.DateTime.serialize(yesterday)
        query_filter = {'updatedAt_Lt': filter_date}
        search_filter = {'updated_at__lt': filter_date}

        data = all_articles_query(
            query_filter=query_filter, search_filter=search_filter)
        query = data['query']
        expect = data['expect']

        result = post_query(query)

        self.assertEqual(result, expect)
