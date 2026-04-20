from pathlib import Path

import setuptools

with Path("README.md").open() as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-local-mail-viewer',
    version='0.0.1',
    packages=setuptools.find_packages(
        exclude=["local_mail_viewer_sample", "*manage.py"]
    ),
    include_package_data=True,
    package_data={
        "local_mail_viewer": [
            "templates/local_mail_viewer/*.html",
            "locale/*/LC_MESSAGES/*",
        ],
    },
    description='A local mail viewer for Django.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Christian Wiegand',
    license='MIT',
    url='https://github.com/christianwgd/django-local-mail-viewer',
    keywords=['django','email', 'develop'],
    install_requires=[
        'django',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
