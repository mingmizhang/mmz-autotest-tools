package com.dp.mingmi.pigeontest;

/**
 * Created by zhangmingmi on 16/8/25.
 */
import com.dp.arts.client.SearchService;
import com.dp.arts.client.request.Request;
import com.dp.arts.client.response.Response;
import com.dp.arts.common.request.RequestParser;

import java.util.List;
import java.util.concurrent.CountDownLatch;

/**
 * Created by zhangmingmi on 16/8/24.
 */
public class SendRequest implements Runnable {

    SearchService searchService;
    private List<String> list;
    CountDownLatch countDownLatch;
    int looptime;
    public SendRequest(List<String> list,SearchService searchService,CountDownLatch countDownLatch,int looptime){
        this.list=list;
        this.searchService = searchService;
        this.countDownLatch = countDownLatch;
        this.looptime = looptime;
    }


    public void run() {
        System.out.print("Start Sending Request!!!'\n'");
        //for (int i = 0; i < 5; i++) {
        sendreq(list,looptime);
        countDownLatch.countDown();
        // }
    }

    public void sendreq(List<String> query_list,int looptime) {
        RequestParser request = new RequestParser();
        //List<String> query_list = new ArrayList<String>();
        //RequestGenerate requestGenerate = new RequestGenerate();
        //query_list = requestGenerate.read_file_to_list("/Users/zhangmingmi/Desktop/query.log");
        for (int j=0;j<looptime;j++) {
            for (int i = 0; i < query_list.size(); i++) {
                Request req = request.parse(query_list.get(i));
                Response response = searchService.search(req);
                System.out.println("The request status is : " + response.getStatus());
            }
        }
    }
}