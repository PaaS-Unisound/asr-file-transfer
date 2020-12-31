1、修改src/main/java/com/unisound/iot/afasr/demo/UtserviceDemo.java代码中的appkey和secet为在云知声AI开放平台(https://ai.unisound.com/controls)申请的
2、直接运行com.unisound.iot.afasr.demo.UtserviceDemo的main方法
3、如无IDE,可直接使用maven打包，依赖JDK8和maven3.6以上版本，具体安装方法自行搜索
4、安装JDK和maven后，在asr-audio-file-demo/目录下执行 mvn clean package
5、进入到target/目录下，运行java -jar asr-audio-file-demo.jar