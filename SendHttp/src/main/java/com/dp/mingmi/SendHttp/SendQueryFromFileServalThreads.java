package com.dp.mingmi.SendHttp;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;

import java.io.IOException;
import java.util.List;

/**
 * Created by zhangmingmi on 16/9/5.
 */
public class SendQueryFromFileServalThreads implements Runnable{
    private int number = 1;
    List<String> url;

    public List<String> getUrl() {
        return url;
    }

    public void setUrl(List<String> url) {
        this.url = url;
    }

    public SendQueryFromFileServalThreads(List<String> url) {
        this.url = url;
    }

    public void run() {
        System.out.print("Start Sending Http Request!!!'\n'");
        for (int i = 0; i < 5; i++) {
            System.out.print(number + "\n");
            number = number + 1;
            try {
                for(int index=0;index<getUrl().size();index++)
                {
                    sendquery("http://******:4053/search/shop?"+getUrl().get(index));
                    //System.out.println("http://******:4053/search/shop?"+getUrl().get(index));
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }


    }

    public void sendquery(String get_url) throws IOException {
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
        String file_path="/Users/zhangmingmi/Desktop/query.log";
        ReadQueryFileToLIst read_query=new ReadQueryFileToLIst();
        List <String> query_list= read_query.read_file_to_list(file_path);
        SendQueryFromFileServalThreads sendtest = new SendQueryFromFileServalThreads(query_list);
        //Sendhttpmultithread test = new Sendhttpmultithread("http://******:4053/search/shop?query=term(cityid,12)");
        new Thread(sendtest).start();
        new Thread(sendtest).start();
        new Thread(sendtest).start();
    }
}
