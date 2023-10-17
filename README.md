# Django project base

A collection of functionalities that are common to most projects we do.

- account management
- project management
- notifications (both to users and to apps)
- tagging
- background job processing
- roles & permissions
- profiling

This project is in VERY early development stage. Some of the functionalities are not even developed yet, some need 
major rework, but some, surprisingly, should work pretty well already. An example of pretty well functioning ones is 
account management.

## Example project

For running example django project prepare python environment and run (run in repository root):

```bash 
$ pip install -r requirements.txt
$ python manage.py runserver
```

## Documentation

Run command in repository root:

```bash 
$ npm run docs:dev
```

The dev server should be running at http://localhost:5173. Visit the URL in your browser to read documentation!

To generate pdf file. Run:

```bash 
$ npm run export-pdf  
```

Pdf file is located in docs/pdf folder.
