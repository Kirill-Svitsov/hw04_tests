[![GitHub](https://img.shields.io/badge/GitHub-Kirill--Svitsov-blue)](https://github.com/Kirill-Svitsov)
# Django Tests

This project was created for learning and practicing testing in Django.

## Testing Models

The models of the `posts` application in Yatube were tested. Methods `__str__` were added to the `Post` and `Group` classes:
- For the `Post` class, the `__str__` method displays the first fifteen characters of the post: `post.text[:15]`.
- For the `Group` class, the `__str__` method displays the group's name.

The correct display of the `__str__` field value in model objects was also verified.

## Testing URLs

The accessibility of pages and the matching of template names in the `Posts` application of the Yatube project were checked. Access rights were taken into account. It was also checked that a request to a non-existent page returns a 404 error.

## Testing namespace:name and templates

Tests were written to check the use of correct html templates in view functions.

## Context Testing

It was checked whether the `context` dictionary passed to the template during the call corresponds to expectations.

## Additional check when creating a post

It was checked that when creating a post with specifying a group, this post appears:
- On the main page of the site
- On the page of the selected group
- In the user's profile

It was also checked that this post did not end up in a group for which it was not intended.

## Technology Stack

- Django
- Python
- Pytest

## Running Tests

To run the tests, execute the following commands:

```
(venv)...Dev/hw04_tests/yatube$ python manage.py test
(venv)...Dev/hw04_tests$ pytest
```

