import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Django project base",
  description: "This project removes the boilerplate associated with project and user handling.",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Quick start guide', link: '/introduction' }
    ],

    sidebar: [
      {
        text: 'Quick start guide',
        items: [
          { text: 'Introduction', link: '/introduction' },
          { text: 'Installation', link: '/installation' },
          { text: 'Settings options', link: '/settings' },
          { text: 'Tags', link: '/tags' },
          { text: 'Fields', link: '/fields' },
          { text: 'Middleware', link: '/middleware' },
          { text: 'Modules', link: '/modules' },
          { text: 'Swagger', link: '/swagger' },
          { text: 'Open API', link: '/open-api' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/velis74/django-project-base' }
    ]
  }
})
