# CLAUDE.md

## Releasing to PyPI

Releases are published by `.github/workflows/publish.yml` when a tag starting
with `v` is pushed. Do not upload from a local machine.

```sh
uv version --bump patch   # or minor / major
git commit -am "Release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push && git push --tags
```

The workflow checks that the tag matches `version` in `pyproject.toml`, runs
pytest, then runs `uv build --no-sources` and `uv publish`. Follow it with
`gh run watch`, then confirm the upload at
https://pypi.org/pypi/camminady-altair-theme/X.Y.Z/json (the project-level JSON
and page are cached and can lag behind by a few minutes).

### Trusted publishing

PyPI accepts uploads only from this workflow through trusted publishing, so no
API token is stored anywhere. The publisher registered on PyPI (project
settings → Publishing) is:

| Field       | Value                    |
|-------------|--------------------------|
| Owner       | `thomascamminady`        |
| Repository  | `camminady_altair_theme` |
| Workflow    | `publish.yml`            |
| Environment | `pypi`                   |

Renaming the workflow file or the environment breaks publishing until the
publisher on PyPI is updated to match.

### Notes

- A tag only triggers a release if the commit it points to contains
  `publish.yml`. Version 0.2.0 was tagged before the workflow existed and was
  never published, so the first release through the workflow was 0.2.1.
- PyPI never accepts the same version twice, even after a release is deleted.
  If a release fails after the upload, bump the version rather than reusing it.
