import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { md3 } from 'vuetify/blueprints'

// Material Design 3 主题配置
const customTheme = {
  dark: false,
  colors: {
    background: '#FFFBFE',
    surface: '#FFFBFE',
    'surface-variant': '#E7E0EC',
    'on-surface-variant': '#49454F',
    primary: '#6750A4',
    'primary-container': '#EADDFF',
    'on-primary': '#FFFFFF',
    'on-primary-container': '#21005D',
    secondary: '#625B71',
    'secondary-container': '#E8DEF8',
    'on-secondary': '#FFFFFF',
    'on-secondary-container': '#1D192B',
    tertiary: '#7D5260',
    'tertiary-container': '#FFD8E4',
    'on-tertiary': '#FFFFFF',
    'on-tertiary-container': '#31111D',
    error: '#BA1A1A',
    'error-container': '#FFDAD6',
    'on-error': '#FFFFFF',
    'on-error-container': '#410002',
    outline: '#79747E',
    'outline-variant': '#CAC4D0',
    'inverse-surface': '#313033',
    'inverse-on-surface': '#F4EFF4',
    'inverse-primary': '#D0BCFF'
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
