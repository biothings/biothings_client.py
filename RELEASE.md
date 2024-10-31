
# RELEASE

## This is the procedure we use for "biothings_client" package release

 1. requires both `build` and `twine` packages installed

    ```bash
    pip install build twine
    ```

 2. Update version number in [pyproject.toml](pyproject.toml).

 3. Check and update other sections of [pyproject.toml](pyproject.toml) if needed (dependencies, metadata etc.).

 4. Build the package locally:

    ```bash
    python -m build
    ```

 5. Test the package built locally:

    ```bash
    pip install dist/biothings_client-0.3.0-py2.py3-none-any.whl
    ```

   And run any local test as needed.

 6. Prepare github repo for the release:

    * Create a tag for each released version (with "v" prefix):

      ```bash
      git tag -a "v0.3.0" -m "tagging v0.3.0 for release"
      ```

    * If everything looks good, push to the remote:

      ```bash
      git push --tags
      ```

 7. Upload to PyPI:

    ```bash
    twine upload dist/*
    ```

    Note: this step needs to be done by @newgene under ["newgene" PyPI account](https://pypi.org/user/newgene/) or any authorized PyPI user.
