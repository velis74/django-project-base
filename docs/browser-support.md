# Browser support

You can add browser check to your webpage. Visitors with outdated browser will be informed that they should
update their browser to get secure and working webpage experience.

To enable browser support, add following script tag to your main html file header.

```html
<head>
    ...
    <script type="module" crossorigin src="{% static 'browser-update/browser-update.js' %}"></script>
    ...
</head>
```