package com.unisound.iot.afasr.demo;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.io.FileUtils;

import java.io.*;
import java.text.DecimalFormat;
import java.util.*;
import java.util.Map.Entry;

/**
 * 音频文件转写demo
 */
public class UtserviceDemo {
	public static String host = "http://af-asr.hivoice.cn//utservice/v2";
	private static String userId = "test_123123";
    static String appkey = "************************";
	static String secret = "************************";

	// 待转写文件路径
	static  String file = "audio/";

	// 输出日志路径
	private static String logPath = "";
	// 待转写文件格式
	private static String format = "wav";

	public static void main(String[] args) {
		try {
			File in = new File(file);
			if (in.isDirectory()){
				List<String> files = getListFromDirectory(in);
				for (String file :files){
					try {
						testAppendUpload(file, format);
					} catch (IOException e) {
						e.printStackTrace();
					}
				}
			}else{
				testAppendUpload(file, format);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static long testAppendUpload(String file, String format) throws IOException {

        String textId =null;
        String ret;
		ret = appendUploadInit(host);
		System.out.println(ret);
		textId = JSONObject.parseObject(ret).getString(PARAM_NAME_TEXTID);

		String md5 = null;
		try {
            md5 = SystemUtils.getMd5Hex(new FileInputStream(file));
			System.out.println("md5:"+md5);
			ret = appendUploadUpload(host, file, textId, format, md5);
			System.out.println(ret);
			ret = appendUploadGetStatus(host, textId);
			System.out.println(ret);

		} catch (Exception e) {
			e.printStackTrace();
		}

		ret = appendUploadFinish(host, textId, format, "other", md5);
		System.out.println(ret);

		String result = getText(host, textId);
		System.out.println(result);
		JSONObject jo = JSONObject.parseObject(result);

		while(!isEnd(jo)){
			SystemUtils.sleep(3000);
			result = getText(host, textId);
			System.out.println(result);
			jo = JSONObject.parseObject(result);
		}

		// 打印结果到文件
		String[] tmp = file.split(File.pathSeparator);
		String[] s = tmp[tmp.length-1].split("\\.");
		File o = new File(logPath + s[0] +".txt");

		JSONArray array = jo.getJSONArray("results");
		StringBuilder builder = new StringBuilder();
		for (int i=0; i<array.size(); i++){
			builder.append(array.getJSONObject(i).getString("text"));
		}
		builder.append("\r\n\r\n")
				.append("********带时间戳的详细信息**********\r\n")
				.append(result);

		FileUtils.writeStringToFile(o,builder.toString(),"UTF-8");

		//生成字幕文件
		File srtFile = new File(logPath + s[0] +".srt");
		srtWriter(jo, srtFile);
		return  jo.getLongValue("cost_time");

	}

	private static void srtWriter(JSONObject result, File srtFile){
		JSONArray array = result.getJSONArray("results");
		StringBuilder builder = new StringBuilder();
		for (int i=0; i<array.size(); i++){
			builder.append(array.getJSONObject(i).getInteger("index") + 1);
			builder.append("\n");
			int start = array.getJSONObject(i).getInteger("start");
			int end = array.getJSONObject(i).getInteger("end");
			builder.append(convertTimeFormat(start));
			builder.append(" --> ");
			builder.append(convertTimeFormat(end));
			builder.append("\n");
			builder.append(array.getJSONObject(i).getString("text"));
			builder.append("\n");
			builder.append("\n");
		}
		try {
			FileUtils.writeStringToFile(srtFile,builder.toString(),"UTF-8");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private static String convertTimeFormat(int millisecond){
		StringBuilder builder = new StringBuilder();
		int ms = millisecond % 1000;
		int s= millisecond / 1000 % 60;
		int min= millisecond / 1000 / 60 % 60;
		int hour = millisecond / 1000 / 60 / 60;
		DecimalFormat df=new DecimalFormat("00");
		DecimalFormat dfms=new DecimalFormat("000");
		builder.append(df.format(hour));
		builder.append(":");
		builder.append(df.format(min));
		builder.append(":");
		builder.append(df.format(s));
		builder.append(",");
		builder.append(dfms.format(ms));
		return builder.toString();
	}
	
	public static boolean isEnd(JSONObject jo){
		if(null == jo){
			return false;
		}
		long progress = jo.getLongValue("progress");
		long duration = jo.getLongValue("duration");
		String status = jo.getString("status");
		
		return "done".equals(status) && (progress == duration);
	}
	
	public static String getText(String baseUrl, String textId){
		String url = baseUrl + "/trans/text?";
		
		Map<String, String> params = new TreeMap<String, String>();
		
		params.put(PARAM_NAME_TEXTID, textId);
		params.put(PARAM_NAME_APPKEY, appkey);
		params.put(PARAM_NAME_TIMESTAMP, System.currentTimeMillis() + "");
		params.put(PARAM_NAME_SIGNATURE, buildSign(secret, params));
		
		String reqUrl = buildReqUrl(url, params);

		byte[] ret = new byte[500];
		String strRet = new String(SystemUtils.httpGet(reqUrl, ret,true));
		return strRet;
	}

	public static String appendUploadInit(String baseUrl){
		try {
			String url = baseUrl + "/trans/append_upload/init?";

			Map<String, String> params = new TreeMap<String, String>();

			params.put(PARAM_NAME_APPKEY, appkey);
			params.put(PARAM_NAME_USER, userId);
			params.put(PARAM_NAME_TIMESTAMP, System.currentTimeMillis() + "");
			params.put(PARAM_NAME_SIGNATURE, buildSign(secret, params));

			String reqUrl = buildReqUrl(url, params);

			byte[] data = SystemUtils.httpPost(reqUrl, null, null, true);

			return new String(data);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}
	public static String appendUploadUpload(String baseUrl, String fileName, String textId, String format, String md5){
		try {
			String url = baseUrl + "/trans/append_upload/upload?";

			Map<String, String> params = new TreeMap<String, String>();

			params.put(PARAM_NAME_APPKEY, appkey);
			params.put(PARAM_NAME_USER, userId);
			params.put(PARAM_NAME_TEXTID, textId);
			params.put(PARAM_NAME_MD5, md5);
			params.put(PARAM_NAME_AUDIOTYPE, format);
			params.put(PARAM_NAME_TIMESTAMP, System.currentTimeMillis() + "");
			params.put(PARAM_NAME_SIGNATURE, buildSign(secret, params));

			String reqUrl = buildReqUrl(url, params);

			byte[] data = SystemUtils.httpPost(reqUrl, SystemUtils.stream2Bytes(new FileInputStream(fileName)), null, true);

			return new String(data);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}
	public static String appendUploadFinish(String baseUrl, String textId, String format, String domain, String md5){
		try {
			String url = baseUrl + "/trans/transcribe?";

			Map<String, String> params = new TreeMap<String, String>();

			params.put(PARAM_NAME_APPKEY, appkey);
			params.put(PARAM_NAME_USER, userId);
			params.put(PARAM_NAME_TEXTID, textId);
			params.put(PARAM_NAME_AUDIOTYPE, format);
			params.put(PARAM_NAME_DOMAIN, domain);
			params.put(PARAM_NAME_MD5, md5);
			params.put(PARAM_NAME_PUNCTION, "beauty");
			params.put(PARAM_NAME_NUM_CONVERT, "true");
			params.put(PARAM_NAME_TIMESTAMP, System.currentTimeMillis() + "");
			params.put(PARAM_NAME_SIGNATURE, buildSign(secret, params));

			String reqUrl = buildReqUrl(url, params);

			byte[] data = SystemUtils.httpPost(reqUrl, null, null, true);

			return new String(data);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}

	public static String appendUploadGetStatus(String baseUrl, String textid){
		try {
			String url = baseUrl + "/trans/append_upload/status?";

			Map<String, String> params = new TreeMap<String, String>();

			params.put(PARAM_NAME_APPKEY, appkey);
			params.put(PARAM_NAME_TEXTID, textid);
			params.put(PARAM_NAME_TIMESTAMP, System.currentTimeMillis() + "");
			params.put(PARAM_NAME_SIGNATURE, buildSign(secret, params));

			String reqUrl = buildReqUrl(url, params);

			byte[] data = SystemUtils.httpPost(reqUrl, null, null, true);

			return new String(data);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}

	/**
	 * 创建请求的 url
	 * @param url
	 * @param params
	 * @return
	 */
	public static String buildReqUrl(String url, Map<String, String> params) {
		StringBuffer ret = new StringBuffer(url);
		
		for(String key : params.keySet()){
			ret.append(key).append('=').append(params.get(key)).append('&');
		}
		
		if(ret.charAt(ret.length() - 1) == '&'){
			return ret.substring(0, ret.length() - 1);
		}
		
		return ret.toString();
	}

	private static List<String> getListFromDirectory(File file) {
		List<String> list = new ArrayList<String>();
		File[] files = file.listFiles();
		for(int i = 0; i < files.length; i++){
			if(files[i].isFile()){
				list.add(files[i].getPath());
			}
		}
		return list;
	}
	/**
	 * 签名校验
	 * @param
	 * @param params
	 * @throws
	 */
	public static String buildSign(String secret, Map<String, String> params) {
		StringBuffer signStr = new StringBuffer(secret);
		for(Entry<String, String> entry : params.entrySet()){
			if(!PARAM_NAME_SIGNATURE.equals(entry.getKey())){
				signStr.append(entry.getValue());
			}
		}
		
		signStr.append(secret);
		
		return SystemUtils.encryptSHA1(signStr.toString()).toUpperCase();
		
	}
	
	public static  final String PARAM_NAME_USER = "userid";

	public static final String PARAM_NAME_AUDIOTYPE = "audiotype";

	public static final String PARAM_NAME_DOMAIN = "domain";

	public static final String PARAM_NAME_APPKEY = "appkey";

	public static final String PARAM_NAME_TIMESTAMP = "timestamp";

	public static final String PARAM_NAME_SIGNATURE = "signature";

	public static final String PARAM_NAME_TEXTID = "task_id";

	public static final String PARAM_NAME_MD5 = "md5";

	public static final String PARAM_NAME_CALL_BACK_URL = "callbackurl";

	public static final String PARAM_NAME_WORD_INFO = "word_info";

	public static final String PARAM_NAME_PUNCTION= "punction";

	public static final String PARAM_NAME_NUM_CONVERT= "num_convert";

}
