import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { md3 } from 'vuetify/blueprints'

// Material Design 3 主题配置 - 翡翠绿主题
const customTheme = {
  dark: false,
  colors: {
    background: '#FAFFFE',
    surface: '#FAFFFE',
    'surface-variant': '#E0F2EC',
    'on-surface-variant': '#49454F',
    primary: '#15AD66', // 翡翠绿 RGB(21,173,102)
    'primary-container': '#B8F5D8',
    'on-primary': '#FFFFFF',
    'on-primary-container': '#00391A',
    secondary: '#4F6B5A',
    'secondary-container': '#D1E7DC',
    'on-secondary': '#FFFFFF',
    'on-secondary-container': '#0C1F17',
    tertiary: '#3A6569',
    'tertiary-container': '#BEE9F0',
    'on-tertiary': '#FFFFFF',
    'on-tertiary-container': '#001F22',
    error: '#BA1A1A',
    'error-container': '#FFDAD6',
    'on-error': '#FFFFFF',
    'on-error-container': '#410002',
    outline: '#6F7972',
    'outline-variant': '#BFC9C2',
    'inverse-surface': '#2C312E',
    'inverse-on-surface': '#ECF2EE',
    'inverse-primary': '#9CD8AC',
    success: '#15AD66',
    warning: '#F57C00',
    info: '#1976D2'
  }
}

export default createVuetify({
  blueprint: md3,
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
  theme: {
    defaultTheme: 'customTheme',
    themes: {
      customTheme
    }
  },
  defaults: {
    VCard: {
      flat: true,
      border: true
    },
    VBtn: {
      style: 'text-transform: none;'
    }
  }
})
