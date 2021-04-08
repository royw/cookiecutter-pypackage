{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}

{% if is_open_source %}
<p align="center">
<a href="https://pypi.python.org/pypi/{{ cookiecutter.project_slug }}">
    <img src="https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg"
        alt = "Release Status">
</a>

<a href="https://travis-ci.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}">
    <img src="https://img.shields.io/travis/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.svg" alt="Build Status">
</a>

<a href="https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/{{ cookiecutter.project_slug | replace("_", "-") }}/badge/?version=latest" alt="Documentation Status">
</a>
{% if cookiecutter.add_pyup_badge == 'y' %}
<a href="https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/">
<img src="https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg" alt="Updates">
</a>
{% endif %}
</p>
{% else %}
{% if cookiecutter.add_pyup_badge == 'y' %}
<p>
<a href="https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/">
<img src="https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg" alt="Updates">
</a>
</p>
{% endif %}
{% endif %}

{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io.
{% endif %}

Features
--------

* TODO

Credits
-------

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.