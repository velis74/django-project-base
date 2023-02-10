declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    gettext: (value: string) => string;
  }
}

declare global {
  interface Window {
    initCookieConsent: () => any
  }
}

export {};
