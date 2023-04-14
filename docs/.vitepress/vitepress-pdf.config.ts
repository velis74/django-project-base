import { defineUserConfig } from 'vitepress-export-pdf'

const routeOrder = [
  '/index.html',
  '/introduction.html',
  '/installation.html',
  '/fields.html',
  '/settings.html',
  '/tags.html',
  '/middleware.html',
  '/modules.html',
  '/swagger.html',
  '/open-api.html',
]

const headerTemplate = `<div style="width: 100%; display: flex; justify-content: center; align-items: center; color: lightgray; border-bottom: solid lightgray 1px; padding-bottom: 10px; font-size: 10px;">
  <span class="title"></span>
</div>`

const footerTemplate = `<div style="width: 100%; display: flex; justify-content: center; align-items: center; color: lightgray; border-top: solid lightgray 1px; padding-top: 10px; font-size: 10px;">
  <span class="pageNumber"></span> - <span class="totalPages"></span>
</div>`


export default defineUserConfig({
  outFile: 'django-project-base.pdf',
  outDir: 'docs/pdf',
  pdfOptions: {
    format: 'A4',
    displayHeaderFooter: true,
    headerTemplate,
    footerTemplate,
    margin: {
      bottom: 70,
      left: 25,
      right: 25,
      top: 70,
    },
  },
  sorter: (pageA, pageB) => {
    const aIndex = routeOrder.findIndex(route => route === pageA.path)
    const bIndex = routeOrder.findIndex(route => route === pageB.path)
    return aIndex - bIndex
  },
})
