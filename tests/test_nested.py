from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


def test_single_linked(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(
        author=author, title="One amazing test post.")
    models.Comment.objects.create(
        post=post, body="This is a test comment.")

    results = {
        "comments": [
            {
                "id": "1",
                "href": "http://testserver/comments/1/",
                "body": "This is a test comment.",
                "links": {
                    "post": "1"
                }
            },
        ],
        "links": {
            "comments.post": {
                "href": "http://testserver/posts/{comments.post}/",
                "type": "posts",
            },
        },
        "linked": {
            "posts": [
                {
                    "id": "1",
                    "href": "http://testserver/posts/1/",
                    "title": "One amazing test post.",
                },
            ],
        },
    }

    response = client.get(reverse("nested-comment-list"))

    assert response.content == dump_json(results)


def test_multiple_linked(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(
        author=author, title="One amazing test post.")
    models.Comment.objects.create(
        post=post, body="This is a test comment.")
    models.Comment.objects.create(
        post=post, body="One more comment.")

    results = {
        "posts": [
            {
                "id": "1",
                "href": "http://testserver/posts/1/",
                "title": "One amazing test post.",
                "links": {
                    "author": "1",
                    "comments": ["1", "2"],
                },
            },
        ],
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}/",
                "type": "people",
            },
            "posts.comments": {
                "href": "http://testserver/comments/{posts.comments}/",
                "type": "comments",
            }
        },
        "linked": {
            "comments": [
                {
                    "id": "1",
                    "href": "http://testserver/comments/1/",
                    "body": "This is a test comment.",
                },
                {
                    "id": "2",
                    "href": "http://testserver/comments/2/",
                    "body": "One more comment.",
                },
            ],
        },
    }

    response = client.get(reverse("nested-post-list"))

    assert response.content == dump_json(results)


def test_multiple_root_entities_linked(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(
        author=author, title="One amazing test post.")
    post2 = models.Post.objects.create(
        author=author, title="A second amazing test post.")
    models.Comment.objects.create(
        post=post, body="This is a test comment.")
    models.Comment.objects.create(
        post=post, body="One more comment.")
    models.Comment.objects.create(
        post=post2, body="One last comment.")

    results = {
        "posts": [
            {
                "id": "1",
                "href": "http://testserver/posts/1/",
                "title": "One amazing test post.",
                "links": {
                    "author": "1",
                    "comments": ["1", "2"],
                },
            },
            {
                "id": "2",
                "href": "http://testserver/posts/2/",
                "title": "A second amazing test post.",
                "links": {
                    "author": "1",
                    "comments": ["3"],
                },
            },
        ],
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}/",
                "type": "people",
            },
            "posts.comments": {
                "href": "http://testserver/comments/{posts.comments}/",
                "type": "comments",
            }
        },
        "linked": {
            "comments": [
                {
                    "id": "1",
                    "href": "http://testserver/comments/1/",
                    "body": "This is a test comment.",
                },
                {
                    "id": "2",
                    "href": "http://testserver/comments/2/",
                    "body": "One more comment.",
                },
                {
                    "id": "3",
                    "href": "http://testserver/comments/3/",
                    "body": "One last comment.",
                },
            ],
        },
    }
    response = client.get(reverse("nested-post-list"))

    assert response.content == dump_json(results)


def test_double_nested_linked(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(
        author=author, title="One amazing test post.")
    models.Comment.objects.create(
        post=post, body="This is a test comment.")

    author.favorite_post = post
    author.save()

    results = {
        "people": [
            {
                "id": "1",
                "href": "http://testserver/people/1/",
                "name": "test",
                "links": {
                    "author": "1",
                    "comments": ["1"],
                    "favorite_post": "1",
                    "liked_comments": [],
                },
            },
        ],
        "links": {
            "people.favorite_post": {
                "href": "http://testserver/posts/{people.favorite_post}/",
                "type": "posts",
            },
            "people.liked_comments": {
                "href": "http://testserver/comments/{people.liked_comments}/",
                "type": "comments"
            },
            "people.posts.author": {
                "href": "http://testserver/people/{people.posts.author}/",
                "type": "people"
            },
            "people.posts.comments": {
                "href": "http://testserver/comments/{people.posts.comments}/",
                "type": "comments"
            },
        },
        "linked": {
            "posts": [
                {
                    "id": "1",
                    "href": "http://testserver/posts/1/",
                    "title": "One amazing test post.",
                    "links": {
                        "author": "1",
                        "comments": ["1"],
                        "favorite_post": "1",
                    },
                },
            ],
            "comments": [
                {
                    "id": "1",
                    "href": "http://testserver/comments/1/",
                    "body": "This is a test comment.",
                },
            ],
        },
    }

    response = client.get(reverse("double-nested-people-list"))

    assert response.content == dump_json(results)
