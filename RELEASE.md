#### This is the procedure we use for "biothings_client" package release

1. requires both `wheel` and `twine` packages installed
   ```
   pip install wheel twine
   ```

2. Update version number in both [base.py](biothings_client/base.py) and [setup.py](setup.py).

3. Check and update [setup.py](setup.py) if needed (dependencies, metadata etc.).

4. Build the package locally:

   ```
   python setup.py sdist bdist_wheel
   ```

5. Test the package built locally:

   ```
   pip install dist/biothings_client-0.2.6-py2.py3-none-any.whl
   ```

   And run any local test as needed.

6. Prepare github repo for the release:

    * Create a tag for each released version (with "v" prefix):
      ```
      git tag -a "v0.2.6" -m "tagging v0.2.6 for release"
      ```

    * If everything looks good, push to the remote:
      ```
      git push --tags
      ```

7. Upload to PyPI:

   ```
   twine upload dist/*
   ```

    Note: this step needs to be done by @newgene under ["newgene" PyPI account](https://pypi.org/user/newgene/) or any authorized PyPI user.
