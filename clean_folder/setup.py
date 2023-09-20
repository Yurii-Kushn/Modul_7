from setuptools import setup

setup(
    name='clean_folder',
    version='0.0.1',
    description='Clean and structure folder',
    url='https://github.com/Yurii-Kushn/Modul_7/blob/master/clean_folder',
    author='Yurii_K',
    author_email='yumk0375@gmail.com',
    packages=['clean_folder'],
    entry_points={'console_scripts': ['clean-folder = clean_folder.clean:main']}
)