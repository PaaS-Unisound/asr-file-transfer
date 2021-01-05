import { defineConfig } from 'umi';

export default defineConfig({
  nodeModulesTransform: {
    type: 'none',
  },
  hash: true,
  publicPath: './',
  history: { type: 'memory' },
  routes: [
    {
      path: '/',
      component: '@/pages/layout/index',
      routes: [
        {
          path: '/asr-audio-file',
          component: '@/pages/layout/asrAudioFile/Test',
          title: '音频文件转写_英语口语评测_语音评测-云知声AI开放平台',
        },
        {
          path: '/',
          redirect: 'asr-audio-file',
        },
      ],
    },
  ],

  theme: {
    'primary-color': '#1564FF',
    'border-radius-base': '4px',
  },
});
