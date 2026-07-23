# Release process

This project publishes `biothings_client` to PyPI when a GitHub release is published.

## Prepare the release

1. Install the package with all test extras and the release tools:

   ```bash
   python -m pip install --upgrade -e ".[caching,dataframe,jsonld,tests]"
   python -m pip install --upgrade build twine black ruff pyright
   ```

2. Update the version in `pyproject.toml` and add the release notes and date to `CHANGES.txt`.

3. Run the checks:

   ```bash
   python -m pytest tests
   python -m black --check biothings_client tests
   ruff check biothings_client tests
   pyright
   ```

4. Build and validate both distributions from a clean directory:

   ```bash
   rm -rf build dist
   python -m build
   python -m twine check dist/*
   ```

5. Install the wheel in a clean virtual environment and run a smoke test:

   ```bash
   python -m venv /tmp/biothings-client-release
   /tmp/biothings-client-release/bin/python -m pip install dist/biothings_client-*.whl
   /tmp/biothings-client-release/bin/python -c \
     'from biothings_client import get_client; print(get_client("gene"))'
   rm -rf /tmp/biothings-client-release
   ```

6. Commit the release preparation, open or merge the pull request, and confirm that the test and build workflows pass on `master`.

## Publish the release

1. Create an annotated version tag with a `v` prefix and push it:

   ```bash
   git tag -a "v0.5.1" -m "tagging v0.5.1 for release"
   git push origin master "v0.5.1"
   ```

2. Publish a GitHub release for the tag. The `PyPI release` workflow builds and uploads the distributions using the configured `PYPI_API_TOKEN` secret.

3. Verify the release on PyPI and test installation from PyPI in a clean environment.

If automated publication is unavailable, an authorized PyPI maintainer can upload the validated distributions manually with `python -m twine upload dist/*`.
