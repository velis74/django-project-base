declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    gettext: (value: string) => string;
  }
}

declare global {
  interface Window {
    initCookieConsent: () => any,
    csrf_token_name: string,
    csrf_token: any
  }
}

export {};
