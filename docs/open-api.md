# Open API

Add folloving to settings.py

::: code-group

```python [myapp/settings.py]

# myapp/settings.py
REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    ...
}
```

:::