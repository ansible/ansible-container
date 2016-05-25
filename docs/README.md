# Ansible Container Docs

Update the documentation by modifying the .rst files found in the *rst* folder.

When you're ready to build, you'll need the following Python sphinx modules installed:

```
pip install sphinx sphinx-autobuild
```

From within the docs folder run `make html`. This will generate HTML files and drop them in 
_build/html. To view the documentation in your local local environment, point a browser to 
file://path-to-your-local/ansible-container/docs/_build/html/index.html, of course modifying 
the path to fit your directory structure.
