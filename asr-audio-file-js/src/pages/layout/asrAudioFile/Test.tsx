import React, { useState, useEffect } from 'react';
import cstyle from '../common.less';
import style from './test.less';
import { Upload, message, Button } from 'antd';
import BMF from 'browser-md5-file';
import sha1 from 'sha1';
import Axios from 'axios';
import { Config, AiCode } from '@/config';

const { Dragger } = Upload;

const userid = 'demoUser';

let timestamp: number;
let signature: string;
let md5: string;
let task_id: string;
let audiotype: string;

export default () => {
  const [current, setCurrent] = useState(0);
  const [filename, setFilename] = useState('');
  const [status, setStatus] = useState(false);
  const [result, setResult] = useState(null);
  const { appKey, secret, path } = Config[AiCode.Audio];
  function getResult() {
    const signature = sha1(
      `${secret}${appKey}${task_id}${timestamp}${secret}`,
    ).toUpperCase();
    doAjax();
    function doAjax() {
      Axios.get(
        `${path}/utservice/v2/trans/text?task_id=${task_id}&appkey=${appKey}&timestamp=${timestamp}&signature=${signature}`,
      )
        .then((res: any) => {
          if (res.data.status === 'done') {
            if (res.data.error_code === 0) {
              setResult(res.data.results);
            }
            setFilename('');
            setStatus(false);
          } else {
            setTimeout(() => {
              doAjax();
            }, 1000);
          }
        })
        .catch((e: any = {}) => {
          setStatus(false);
          message.error(e.message || '转写出现错误！');
        });
    }
  }

  const props: any = {
    name: 'file',
    multiple: false,
    headers: { 'Content-Type': 'application/octet-stream' },
    showUploadList: false,
    style: {
      background: 'transparent',
      width: '548px',
      height: '320px',
      border: 'none',
    },
    accept: '.mp3,.wav',
    beforeUpload(file: any) {
      if (file.type.indexOf('/') < 0) {
        message.warning('请选择mp3、wav类型的文件');
        return false;
      }
      if (
        'opus,wav,amr,m4a,mp3'.split(',').indexOf(
          file.name
            .split('.')
            .pop()
            .toLowerCase(),
        ) < 0
      ) {
        message.warning('请选择mp3、wav类型的文件');
        return false;
      }
      if (file.size > 5 * 1024 * 1024) {
        message.warning('请选择5M以下的文件！');
        return false;
      }
      return file;
    },
    action(file: any) {
      return new Promise((reslove, reject) => {
        audiotype = file.name
          .split('.')
          .pop()
          .toLowerCase();
        timestamp = +new Date();
        signature = sha1(
          `${secret}${appKey}${timestamp}${userid}${secret}`,
        ).toUpperCase();

        Axios.get(`${path}/utservice/v2/trans/append_upload/init`, {
          params: {
            userid,
            timestamp,
            signature,
            appkey: appKey,
          },
        }).then((res: any) => {
          if (res.data.error_code == 0) {
            const bmf = new BMF();
            task_id = res.data.task_id;
            bmf.md5(file, (err: any, md5str: string) => {
              md5 = md5str;
              signature = sha1(
                `${secret}${appKey}${audiotype}${md5}${task_id}${timestamp}${userid}${secret}`,
              ).toUpperCase();

              reslove(
                `${path}/utservice/v2/trans/append_upload/upload?userid=${userid}&md5=${md5}&task_id=${task_id}&audiotype=${audiotype}&appkey=${appKey}&timestamp=${timestamp}&signature=${signature}`,
              );
            });
          } else {
            message.error(res.data.message);
          }
        });
      });
    },
    customRequest: (option: any) => {
      const { action, file } = option;
      const xmlhttp = new XMLHttpRequest();
      xmlhttp.open('POST', action);
      var reader = new FileReader();
      reader.onload = function(e: any) {
        // target.result 该属性表示目标对象的DataURL
        xmlhttp.send(e.target.result);
      };
      reader.readAsArrayBuffer(file);
      xmlhttp.onreadystatechange = () => {
        if (xmlhttp.readyState == 4) {
          if (xmlhttp.status == 200) {
            const result = JSON.parse(xmlhttp.responseText);
            if (result.error_code === 0) {
              setFilename(file.name);
            } else {
              message.error(result.message);
            }
          } else {
          }
        }
      };
    },
  };
  return (
    <div
      style={{
        backgroundColor: '#f7f9fb',
      }}
      className={cstyle.bigBlock}
      id="test"
    >
      <div className={cstyle.title}>产品体验</div>
      <div className={style.boxContainer}>
        <div className={style.box}>
          <div className={cstyle.subTitle}>
            文件上传
            <span style={{ fontSize: 14, color: '#999999' }}>
              （支持mp3、wav且5M内文件，采样率16k/8k，位长16bit，单声道）
            </span>
          </div>
          <div className={style.borderBox}>
            <ul className={style.tabs}>
              <li
                className={`${style.tab} ${current === 0 ? style.active : ''}`}
                onClick={() => setCurrent(0)}
              >
                汉语
              </li>
              <li
                className={`${style.tab} ${current === 1 ? style.active : ''}`}
                onClick={() => setCurrent(1)}
              >
                英语
              </li>
            </ul>
            <div className={style.micbox}>
              <Dragger {...props}>
                <div className={style.imgback}>
                  {!filename && (
                    <div className={style.imgtext}>
                      点击上传或拖拽文件到这里
                    </div>
                  )}
                  {filename && (
                    <div className={style.imgtext}>
                      <div className="ellipsis">{filename}</div>
                      <a style={{ color: '#e7a704' }}>重新上传</a>
                    </div>
                  )}
                </div>
              </Dragger>
              <Button
                type="primary"
                className={style.button}
                disabled={!filename}
                loading={status}
                onClick={() => {
                  let lang = current === 0 ? 'cn' : 'en';
                  const signature = sha1(
                    `${secret}${appKey}${audiotype}other${lang}${md5}${task_id}${timestamp}${userid}${secret}`,
                  ).toUpperCase();

                  Axios.get(
                    `${path}/utservice/v2/trans/transcribe?userid=${userid}&task_id=${task_id}&audiotype=${audiotype}&domain=other&lang=${lang}&md5=${md5}&appkey=${appKey}&timestamp=${timestamp}&signature=${signature}`,
                  ).then((res: any) => {
                    if (res.data.error_code === 0) {
                      setStatus(true);
                      getResult();
                    }
                  });
                }}
              >
                开始转写
              </Button>
            </div>
          </div>
        </div>
        <div className={style.box}>
          <div className={cstyle.subTitle}>识别结果</div>
          <div className={style.borderBox + ' ' + style.result}>
            {result && result.map((r: any) => r.text)}
          </div>
        </div>
      </div>
    </div>
  );
};
