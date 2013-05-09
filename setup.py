from setuptools import setup

setup(
    name='flask-canvas',
    version='0.1',
    keywords='python,facebook,canvas,oauth2',
    url='https://github.com/demianbrecht/flask-canvas',
    license='MIT',
    author='Demian Brecht',
    author_email='demianbrecht@gmail.com',
    description='A Flask extension for Facebook canvas-based apps',
    py_modules=['flask_canvas'],
    include_package_data=True,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
    ])
