# Exercise 1
## What is autograde.yml for? Which commands does it run, and in which folders?

Az `autograde.yml` minden push, pull request vagy kézi indítás esetén lefuttatja
az összes labor automatikus ellenőrzését. A `labs/*/starter` és a `labs/*`
mappákban keresi a `pyproject.toml` fájlt. Mindegyik ilyen projekt mappájában
ellenőrzi az `uv.lock` naprakészségét az `uv lock --check` paranccsal, majd
lefuttatja az `uv sync --locked --all-groups` és az `uv run --frozen pytest -q`
parancsokat.

# Exercise 5