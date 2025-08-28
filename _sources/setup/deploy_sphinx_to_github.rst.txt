Deploying Sphinx Documentation to GitHub
========================================

To automatically publish the **GisFIRE2** documentation to GitHub Pages on each push, follow these steps:

1. **Create the GitHub Actions workflow file**

    In the project root, create the file:

    ``.github.workflows.documentation.yml``

    Add the following workflow definition:

    .. code-block:: yaml

        name: documentation

        on: [push, pull_request, workflow_dispatch]

        permissions:
          contents: write

        jobs:
          docs:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
              - name: Install dependencies
                run: |
                  pip install sphinx sphinx_rtd_theme myst_parser
              - name: Sphinx build
                run: |
                  sphinx-build doc/source _build
              - name: Deploy to GitHub Pages
                uses: peaceiris/actions-gh-pages@v3
                if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
                with:
                  publish_branch: gh-pages
                  github_token: ${{ secrets.GITHUB_TOKEN }}
                  publish_dir: _build/
                  force_orphan: true

    **Important:** Adjust the `sphinx-build doc/source _build` path so it points to your project’s actual Sphinx
    source directory.

2. **Configure GitHub Pages publishing**

    After the workflow is created, configure GitHub Pages to serve content from the ``gh-pages`` branch:

    - Go to your repository’s `Settings → Pages → Build and deployment`.
    - Set the **Source** to **Deploy from a branch**.
    - Select **Branch: gh-pages** and the **root** folder.


3. **Access the published documentation**

    Once configured, the documentation will be automatically built and deployed after each push to the `main` branch.

    The published site will be available at:

    `<https://jaumefigueras.github.io/GisFIRE2/>`_

References
----------

- `GitHub Pages with GitHub Actions — Coderefinery <https://coderefinery.github.io/documentation/gh_workflow/#github-pages>`_
- `Configuring a publishing source for your GitHub Pages site — GitHub Docs <https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site>`_
