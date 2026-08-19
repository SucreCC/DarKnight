/** @type {import('prettier').Config} */
export default {
  printWidth: 100, // 每行代码长度（默认 80）
  tabWidth: 2, // 每个 tab 相当于多少个空格（默认 2）
  useTabs: false, // 是否使用 tab 缩进
  semi: false, // 声明结尾是否使用分号（默认 true）
  vueIndentScriptAndStyle: false,
  singleQuote: true, // 使用单引号（默认 false）
  quoteProps: 'as-needed',
  bracketSpacing: true, // 对象字面量的大括号间使用空格（默认 true）
  trailingComma: 'none', // 多行是否使用拖尾逗号（默认 none）
  jsxSingleQuote: false,
  // 箭头函数参数括号，可选 avoid | always
  // avoid：能省略括号时就省略，例如 x => x
  // always：总是带括号
  arrowParens: 'always',
  insertPragma: false,
  requirePragma: false,
  proseWrap: 'never',
  htmlWhitespaceSensitivity: 'strict',
  endOfLine: 'auto',
  rangeStart: 0
}
