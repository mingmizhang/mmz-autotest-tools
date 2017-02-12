package com.dp.mingmi.SendHttp;

import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.HttpClient;

import java.io.IOException;


/**
 * Created by zhangmingmi on 16/8/22.
 */
public class Sendhttpmultithread implements Runnable {
    private int number = 1;
    private String url;

    public Sendhttpmultithread(String url) {
        this.url = url;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public void run() {
        System.out.print("Start Sending Http Request!!!'\n'");
        for (int i = 0; i < 5; i++) {
            System.out.print(number + "\n");
            number = number + 1;
            try {
                sendhttprequest(getUrl());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }


    }

    public void sendhttprequest(String get_url) throws IOException {
        // 创建HttpClient实例
        HttpClient client = new HttpClient();
        // 创建Get方法实例
        HttpMethod method = new GetMethod(get_url);
        client.executeMethod(method);
        //打印服务器返回的状态
        System.out.println(method.getStatusLine());
        //打印返回的信息
        String Body = method.getResponseBodyAsString();
        //释放连接
        method.releaseConnection();
    }

    public static void main(String[] args) {
        Sendhttpmultithread test = new Sendhttpmultithread("http://192.0.0.0:4053/search/shop?query=term(cityid,12)");
        new Thread(test).start();
        new Thread(test).start();
        new Thread(test).start();
    }

}


