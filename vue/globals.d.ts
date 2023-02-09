declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    gettext: (value: string) => string;
  }
}

export {};
