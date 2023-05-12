import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Django project base",
  description: "This project removes the boilerplate associated with project and user handling.",
  cleanUrls: true,
  ignoreDeadLinks: [
    /^https?:\/\/localhost/,
  ],
  lastUpdated: false,
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      {text: 'Home', link: '/'},
      {text: 'Getting started', link: '/installation'},
      {text: 'Manual', link: '/introduction'}
    ],
    sidebar: [
      {
        text: 'Getting started',
        collapsed: false,
        items: [
          {text: 'Introduction', link: '/introduction'},
          {text: 'Installation', link: '/installation'},
        ]
      },
      {
        text: 'Reference',
        collapsed: false,
        items: [
          {text: 'Project', link: '/project'},
          {text: 'User profile', link: '/user-profile'},
          {text: 'Authentication', link: '/authentication'},
          {text: 'Settings options', link: '/settings'},
          {text: 'Tags', link: '/tags'},
          {text: 'Fields', link: '/fields'},
          {text: 'Performance profiler', link: '/performance-profiler'},
          {text: 'URL variables middleware', link: '/url-variables-middleware'},
          {text: 'Notifications', link: '/notifications'},
          {text: 'Swagger', link: '/swagger'},
          {text: 'Open API', link: '/open-api'},
        ]
      }
    ],
    socialLinks: [
      {icon: 'github', link: 'https://github.com/velis74/django-project-base'}
    ],
    footer: {
      message: 'All rights reserved',
      copyright: 'Copyright © 2021-present Velis d.o.o.'
    },
  }
})
