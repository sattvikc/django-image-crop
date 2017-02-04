from setuptools import find_packages, setup


setup(
    name='django-image-crop',
    version='1.0.0',
    author='Sattvik Chakravarthy',
    author_email='sattvik@gmail.com',
    packages=find_packages(),
    install_requires=[
        'Django',
        'Pillow',
    ],
    include_package_data=True,
    zip_safe=False
)
