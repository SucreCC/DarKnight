export type DocCategoryId = 'notice' | 'faq' | 'tutorial'

export type DocBlock =
  | { type: 'lead'; textKey: string }
  | { type: 'step'; titleKey: string; bodyKey?: string }
  | { type: 'paragraph'; textKey: string }
  | { type: 'downloads'; items: { labelKey: string; url: string }[] }
  | { type: 'note'; textKey: string }
  | { type: 'copySub' }
  | { type: 'importClash' }
  | { type: 'importShadowrocket' }

export interface DocArticle {
  id: string
  category: DocCategoryId
  titleKey: string
  updatedAt: string
  blocks: DocBlock[]
}

export interface DocCategory {
  id: DocCategoryId
  titleKey: string
}

export const CLIENT_DOWNLOADS = {
  clashVergeWinX64:
    'https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.4.7/Clash.Verge_2.4.7_x64-setup.exe',
  clashVergeWinArm64:
    'https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.4.7/Clash.Verge_2.4.7_arm64-setup.exe',
  clashVergeMacArm:
    'https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.4.7/Clash.Verge_2.4.7_aarch64.dmg',
  clashVergeMacIntel:
    'https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.4.7/Clash.Verge_2.4.7_x64.dmg',
  shadowrocket: 'https://apps.apple.com/us/app/shadowrocket/id932747118',
  clashMetaAndroid:
    'https://github.com/MetaCubeX/ClashMetaForAndroid/releases/download/v2.11.26/cmfa-2.11.26-meta-universal-release.apk'
} as const

export const DOC_CATEGORIES: DocCategory[] = [
  { id: 'notice', titleKey: 'portal.docs.category.notice' },
  { id: 'faq', titleKey: 'portal.docs.category.faq' },
  { id: 'tutorial', titleKey: 'portal.docs.category.tutorial' }
]

export const DOC_ARTICLES: DocArticle[] = [
  {
    id: 'must-read',
    category: 'notice',
    titleKey: 'portal.docs.mustRead.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.mustRead.lead' },
      { type: 'paragraph', textKey: 'portal.docs.mustRead.p1' },
      { type: 'paragraph', textKey: 'portal.docs.mustRead.p2' },
      { type: 'paragraph', textKey: 'portal.docs.mustRead.p3' }
    ]
  },
  {
    id: 'shadowrocket-update',
    category: 'notice',
    titleKey: 'portal.docs.shadowrocketNotice.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.shadowrocketNotice.lead' },
      { type: 'paragraph', textKey: 'portal.docs.shadowrocketNotice.p1' },
      {
        type: 'downloads',
        items: [{ labelKey: 'portal.docs.ios.downloadBtn', url: CLIENT_DOWNLOADS.shadowrocket }]
      }
    ]
  },
  {
    id: 'quantumult-x',
    category: 'faq',
    titleKey: 'portal.docs.quantumult.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.quantumult.lead' },
      { type: 'paragraph', textKey: 'portal.docs.quantumult.p1' }
    ]
  },
  {
    id: 'support',
    category: 'faq',
    titleKey: 'portal.docs.support.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.support.lead' },
      { type: 'paragraph', textKey: 'portal.docs.support.p1' }
    ]
  },
  {
    id: 'windows',
    category: 'tutorial',
    titleKey: 'portal.docs.windows.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.windows.lead' },
      { type: 'step', titleKey: 'portal.docs.windows.step1' },
      {
        type: 'downloads',
        items: [
          { labelKey: 'portal.docs.windows.downloadX64', url: CLIENT_DOWNLOADS.clashVergeWinX64 },
          {
            labelKey: 'portal.docs.windows.downloadArm64',
            url: CLIENT_DOWNLOADS.clashVergeWinArm64
          }
        ]
      },
      { type: 'note', textKey: 'portal.docs.windows.note' },
      {
        type: 'step',
        titleKey: 'portal.docs.windows.step2',
        bodyKey: 'portal.docs.windows.step2Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.windows.step3',
        bodyKey: 'portal.docs.windows.step3Body'
      },
      { type: 'copySub' },
      {
        type: 'step',
        titleKey: 'portal.docs.windows.step4',
        bodyKey: 'portal.docs.windows.step4Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.windows.step5',
        bodyKey: 'portal.docs.windows.step5Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.windows.step6',
        bodyKey: 'portal.docs.windows.step6Body'
      }
    ]
  },
  {
    id: 'macos',
    category: 'tutorial',
    titleKey: 'portal.docs.macos.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.macos.lead' },
      { type: 'step', titleKey: 'portal.docs.macos.step1' },
      {
        type: 'downloads',
        items: [
          { labelKey: 'portal.docs.macos.downloadArm', url: CLIENT_DOWNLOADS.clashVergeMacArm },
          { labelKey: 'portal.docs.macos.downloadIntel', url: CLIENT_DOWNLOADS.clashVergeMacIntel }
        ]
      },
      { type: 'step', titleKey: 'portal.docs.macos.step2', bodyKey: 'portal.docs.macos.step2Body' },
      { type: 'step', titleKey: 'portal.docs.macos.step3', bodyKey: 'portal.docs.macos.step3Body' },
      { type: 'importClash' },
      { type: 'copySub' },
      { type: 'step', titleKey: 'portal.docs.macos.step4', bodyKey: 'portal.docs.macos.step4Body' },
      { type: 'step', titleKey: 'portal.docs.macos.step5', bodyKey: 'portal.docs.macos.step5Body' }
    ]
  },
  {
    id: 'ios',
    category: 'tutorial',
    titleKey: 'portal.docs.ios.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.ios.lead' },
      { type: 'step', titleKey: 'portal.docs.ios.step1' },
      {
        type: 'downloads',
        items: [{ labelKey: 'portal.docs.ios.downloadBtn', url: CLIENT_DOWNLOADS.shadowrocket }]
      },
      { type: 'note', textKey: 'portal.docs.ios.note' },
      { type: 'step', titleKey: 'portal.docs.ios.step2', bodyKey: 'portal.docs.ios.step2Body' },
      { type: 'importShadowrocket' },
      { type: 'copySub' }
    ]
  },
  {
    id: 'android',
    category: 'tutorial',
    titleKey: 'portal.docs.android.title',
    updatedAt: '2024/4/19',
    blocks: [
      { type: 'lead', textKey: 'portal.docs.android.lead' },
      { type: 'step', titleKey: 'portal.docs.android.step1' },
      {
        type: 'downloads',
        items: [
          { labelKey: 'portal.docs.android.downloadBtn', url: CLIENT_DOWNLOADS.clashMetaAndroid }
        ]
      },
      { type: 'note', textKey: 'portal.docs.android.note' },
      {
        type: 'step',
        titleKey: 'portal.docs.android.step2',
        bodyKey: 'portal.docs.android.step2Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.android.step3',
        bodyKey: 'portal.docs.android.step3Body'
      },
      { type: 'copySub' },
      {
        type: 'step',
        titleKey: 'portal.docs.android.step4',
        bodyKey: 'portal.docs.android.step4Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.android.step5',
        bodyKey: 'portal.docs.android.step5Body'
      },
      {
        type: 'step',
        titleKey: 'portal.docs.android.step6',
        bodyKey: 'portal.docs.android.step6Body'
      }
    ]
  }
]

export function getDocById(id: string): DocArticle | undefined {
  return DOC_ARTICLES.find((article) => article.id === id)
}
