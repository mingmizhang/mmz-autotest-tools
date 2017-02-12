package com.dp.mingmi.ShopHttp;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONException;
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;

import java.io.IOException;
import java.util.*;

public class CompareHttpResult{
    public static final String STATUS = "status";
    public static final String TOTALHITS = "totalhits";
    public static final String RECORDS = "records";
    public static final String OTHERINFO = "otherinfo";
    private String url;
    private String record_field;
    private String otherinfo_field;

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getRecord_field() {
        return record_field;
    }

    public void setRecord_field(String record_field) {
        this.record_field = record_field;
    }

    public String getOtherinfo_field() {
        return otherinfo_field;
    }

    public void setOtherinfo_field(String otherinfo_field) {
        this.otherinfo_field = otherinfo_field;
    }

    public CompareHttpResult(String url,String record_field,String otherinfo_field){
        this.url=url;
        this.record_field=record_field;
        this.otherinfo_field=otherinfo_field;
    }
    public  String  GetResponseField() throws IOException {
        String Body = SendUrl(getUrl());
        //校验数据是否正确
        JSONObject jsonresponse = ParseJson(Body);
        System.out.print(jsonresponse);
        System.out.println();
        //校验reponse中的最外层的key值
        Set keysets =jsonresponse.keySet();
        for(Iterator<String> iterator = keysets.iterator();iterator.hasNext();){
            System.out.print(iterator.next()+"\n");
        }
        //校验请求返回状态
        String response_status=jsonresponse.get(STATUS).toString();
        System.out.print(jsonresponse.get(STATUS));
        System.out.println();
        //校验请求返回的records总数
        String response_totalhits=jsonresponse.get(TOTALHITS).toString();
        System.out.print(response_totalhits);
        //校验请求的第一条records的regionname字段
        List<String> regionname_value = new ArrayList<String>();
        regionname_value = GetKeyValueInResponse(jsonresponse, RECORDS, getRecord_field());
        for(int i = 0;i < regionname_value.size();i++){
            System.out.print(i);
            System.out.print(regionname_value.get(i));
        }

        //校验请求返回体的otherinfo信息
        String other_value = GetOtherInfoInResponse(jsonresponse,OTHERINFO,getOtherinfo_field());
        return other_value;

    }
    public  String  GetOtherInfoField() throws IOException {
        String Body = SendUrl(getUrl());
        //校验数据是否正确
        JSONObject jsonresponse = ParseJson(Body);
        //校验请求返回状态
        //校验请求返回体的otherinfo信息
        String other_value = GetOtherInfoInResponse(jsonresponse,OTHERINFO,getOtherinfo_field());
        return other_value;

    }
    public  List<String>  GetRecordField(String getRecord_field) throws IOException {
        String Body = SendUrl(getUrl());
        //校验数据是否正确
        JSONObject jsonresponse = ParseJson(Body);
        //校验请求返回状态
        //校验请求返回体的Record信息
        List<String> Record_List = new ArrayList<String>();
        Record_List = GetKeyValueInResponse(jsonresponse, RECORDS, getRecord_field());
        return Record_List;

    }
    public Boolean at_Least_One_shopname_contains(String shopname,List<String> Record_List) throws IOException {
        Record_List = GetRecordField(getRecord_field());
        Boolean Flag = false;
        for(int i = 0;i < Record_List.size();i++){
            if ((Record_List.get(i)).equals(shopname));
            {
                Flag = true;
                return Flag;
            }
        }
        return Flag;

    }
    public static String SendUrl(String get_url) throws IOException {
        // 创建HttpClient实例
        HttpClient client = new HttpClient();
        // 创建Get方法实例
        HttpMethod method = new GetMethod(get_url);
        client.executeMethod(method);
        //打印服务器返回的状态
        System.out.println(method.getStatusLine());
        //打印返回的信息
        String Body = method.getResponseBodyAsString();
        //System.out.println(method.getResponseBody());
        //System.out.println(method.getResponseBodyAsString());
        //System.out.print(Body);
        //释放连接
        method.releaseConnection();
        return Body;
    }

    public static JSONObject ParseJson(String jsontext){
        //String字符串转化为json对象
        JSONObject json_response = null;
        try{

            json_response = JSON.parseObject(jsontext);
        }catch (JSONException e)
        {
            System.out.println("String To Json ERROR");
        }
        return json_response;
    }

    public static List<String> GetKeyValueInResponse(JSONObject json,String response_key,String key) {
        List<String> key_value = new ArrayList<String>();
        List<Object> string_record = (List<Object>) json.get(response_key);
        //System.out.print(string_record.get(1));
        Map<String,String> map_record = new HashMap<String,String>();
        for (Object s : string_record)
        {
            //System.out.println();
            //System.out.print(s);
            JSONObject json_record = ParseJson(s.toString());
            String value=json_record.get(key).toString();
            key_value.add(value);
            //System.out.println();
            //System.out.print(value);
        }
        return key_value;
    }
    public static String GetOtherInfoInResponse(JSONObject json,String response_otherinfo,String key){
        Map<String,String> otherinfo_value = new HashMap<String,String>();
        Map<String,Object> Map_otherinfo = (Map<String,Object>) json.get(response_otherinfo);
        for (Map.Entry<String, Object> entry : Map_otherinfo.entrySet()) {
            String k = entry.getKey();
            Object v = entry.getValue();
            if (k.equals(key)){
                System.out.println("k:" + k + ",v:" + v);
                return v.toString();
            }

        }
        return "";
    }

    public static void main(String[] args) throws IOException {
        CompareHttpResult result = new CompareHttpResult("http://******:4053/search/shop?query=term(cityid,1)","regionname","bizip");
        System.out.println(result.GetResponseField());

    }

}
