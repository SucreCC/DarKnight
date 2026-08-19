/** @type {import('stylelint').Config} */
export default {
  root: true,
  plugins: ['stylelint-order'],
  // customSyntax 由 stylelint-config-standard-scss 提供（postcss-scss），
  // .vue / .html 在下方 overrides 里换成 postcss-html。
  extends: ['stylelint-config-standard-scss'],
  rules: {
    'selector-pseudo-class-no-unknown': [
      true,
      {
        // export：src/styles/global.module.scss 用 `:export` 把 scss 变量转导给 JS（useDesign 消费）。
        ignorePseudoClasses: ['global', 'deep', 'export']
      }
    ],
    // src/styles/global.module.scss 的 `:export` 块里 namespace / elNamespace 不是 CSS 属性。
    'property-no-unknown': [
      true,
      {
        ignoreProperties: ['namespace', 'elNamespace']
      }
    ],
    // yudao 的 src/styles/*.scss 注释前不留空行；src/styles/index.scss 的 @use 带 .scss 后缀。
    'scss/double-slash-comment-empty-line-before': null,
    'scss/load-partial-extension': null,
    // yudao 的 src/styles/var.css 每个自定义属性之间都留空行，且注释紧贴前一行。
    'custom-property-empty-line-before': null,
    'comment-empty-line-before': null,
    // yudao 的 src/styles/var.css 用单冒号写 `:after` / `:before`。
    'selector-pseudo-element-colon-notation': null,
    // scss 方言下由 scss/at-rule-no-unknown 接管。
    'at-rule-no-unknown': null,
    'media-query-no-invalid': null,
    'function-no-unknown': null,
    'scss/function-no-unknown': null,
    'no-empty-source': null,
    'named-grid-areas-no-invalid': null,
    'no-descending-specificity': null,
    'font-family-no-missing-generic-family-keyword': null,
    // 类名里含 #{$namespace} 插值，无法满足 standard-scss 的 kebab-case 模式。
    'selector-class-pattern': null,
    'keyframes-name-pattern': null,
    'scss/dollar-variable-pattern': null,
    'scss/percent-placeholder-pattern': null,
    'rule-empty-line-before': [
      'always',
      {
        ignore: ['after-comment', 'first-nested']
      }
    ],
    'unit-no-unknown': [
      true,
      {
        ignoreUnits: ['rpx']
      }
    ],
    'order/order': [
      [
        'dollar-variables',
        'custom-properties',
        'at-rules',
        'declarations',
        {
          type: 'at-rule',
          name: 'supports'
        },
        {
          type: 'at-rule',
          name: 'media'
        },
        'rules'
      ],
      {
        severity: 'warning'
      }
    ],
    // 声明块内 CSS 属性的排列顺序，保持 error 严格度。
    'order/properties-order': [
      [
        'position',
        'top',
        'right',
        'bottom',
        'left',
        'z-index',
        'display',
        'float',
        'width',
        'height',
        'max-width',
        'max-height',
        'min-width',
        'min-height',
        'padding',
        'padding-top',
        'padding-right',
        'padding-bottom',
        'padding-left',
        'margin',
        'margin-top',
        'margin-right',
        'margin-bottom',
        'margin-left',
        'margin-collapse',
        'margin-top-collapse',
        'margin-right-collapse',
        'margin-bottom-collapse',
        'margin-left-collapse',
        'overflow',
        'overflow-x',
        'overflow-y',
        'clip',
        'clear',
        'font',
        'font-family',
        'font-size',
        'font-smoothing',
        'osx-font-smoothing',
        'font-style',
        'font-weight',
        'hyphens',
        'src',
        'line-height',
        'letter-spacing',
        'word-spacing',
        'color',
        'text-align',
        'text-decoration',
        'text-indent',
        'text-overflow',
        'text-rendering',
        'text-size-adjust',
        'text-shadow',
        'text-transform',
        'word-break',
        'word-wrap',
        'white-space',
        'vertical-align',
        'list-style',
        'list-style-type',
        'list-style-position',
        'list-style-image',
        'pointer-events',
        'cursor',
        'background',
        'background-attachment',
        'background-color',
        'background-image',
        'background-position',
        'background-repeat',
        'background-size',
        'border',
        'border-collapse',
        'border-top',
        'border-right',
        'border-bottom',
        'border-left',
        'border-color',
        'border-image',
        'border-top-color',
        'border-right-color',
        'border-bottom-color',
        'border-left-color',
        'border-spacing',
        'border-style',
        'border-top-style',
        'border-right-style',
        'border-bottom-style',
        'border-left-style',
        'border-width',
        'border-top-width',
        'border-right-width',
        'border-bottom-width',
        'border-left-width',
        'border-radius',
        'border-top-right-radius',
        'border-bottom-right-radius',
        'border-bottom-left-radius',
        'border-top-left-radius',
        'border-radius-topright',
        'border-radius-bottomright',
        'border-radius-bottomleft',
        'border-radius-topleft',
        'content',
        'quotes',
        'outline',
        'outline-offset',
        'opacity',
        'filter',
        'visibility',
        'size',
        'zoom',
        'transform',
        'box-align',
        'box-flex',
        'box-orient',
        'box-pack',
        'box-shadow',
        'box-sizing',
        'table-layout',
        'animation',
        'animation-delay',
        'animation-duration',
        'animation-iteration-count',
        'animation-name',
        'animation-play-state',
        'animation-timing-function',
        'animation-fill-mode',
        'transition',
        'transition-delay',
        'transition-duration',
        'transition-property',
        'transition-timing-function',
        'background-clip',
        'backface-visibility',
        'resize',
        'appearance',
        'user-select',
        'interpolation-mode',
        'direction',
        'marks',
        'page',
        'set-link-source',
        'unicode-bidi',
        'speak'
      ]
    ]
  },
  ignoreFiles: ['**/*.js', '**/*.jsx', '**/*.tsx', '**/*.ts'],
  overrides: [
    {
      files: ['*.vue', '**/*.vue', '*.html', '**/*.html'],
      extends: ['stylelint-config-recommended-vue', 'stylelint-config-html'],
      rules: {
        'keyframes-name-pattern': null,
        'selector-class-pattern': null,
        'no-duplicate-selectors': null,
        'selector-pseudo-class-no-unknown': [
          true,
          {
            ignorePseudoClasses: ['deep', 'global', 'export']
          }
        ],
        'selector-pseudo-element-no-unknown': [
          true,
          {
            ignorePseudoElements: ['v-deep', 'v-global', 'v-slotted']
          }
        ],
        // TagsView 用到的 WebKit 私有 mask 语法有效，但 Stylelint 不能完整识别。
        'declaration-property-value-no-unknown': [
          true,
          {
            ignoreProperties: {
              '-webkit-mask-box-image': [/.*/]
            }
          }
        ]
      }
    }
  ]
}
