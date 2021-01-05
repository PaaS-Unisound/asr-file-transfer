export enum AiCode {
  Audio = 'asr-audio-file',
}

export const Config = {
  [AiCode.Audio]: {
    appKey: 'appKey',
    secret: 'secret',
    path: 'servicePath',
  },
};
