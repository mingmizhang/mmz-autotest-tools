package com.dp.mingmi.ShopHttp;
import java.lang.*;
import java.util.HashMap;
import java.util.Iterator;
import java.util.*;
import java.util.Map;
import java.sql.*;

public class DataProviderSQL implements Iterator<List<Map<String,String>>> {
    //public static final String ArtsIT_ip = "128.7.7.32";
    //public static final String ArtsIT_username = "test";
    //public static final String ArtsIT_password = "test";
    public ResultSet rs;
    public ResultSetMetaData rd;

    public DataProviderSQL(String sql,String ArtsIT_ip,String port,String baseName,String ArtsIT_username,String ArtsIT_password) throws ClassNotFoundException,SQLException {
        try {
            //加载MySql的驱动类
            Class.forName("com.mysql.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("找不到驱动程序类 ，加载驱动失败！");
            e.printStackTrace();
        }
        String con_url=String.format("jdbc:mysql://%s:%s/%s", ArtsIT_ip, port, baseName);
        Connection conn = DriverManager.getConnection(con_url, ArtsIT_username, ArtsIT_password);
        Statement createStatement = conn.createStatement();
        // 执行SQL命令，并返回符合条件的记录
        rs = createStatement.executeQuery(sql);
        rd = rs.getMetaData();
    }

    public boolean hasNext() {
        boolean flag = false;
        try {
            flag = rs.next();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return flag;

    }

    public List<Map<String,String>> next(){

        List<Map<String,String>> several_row=new ArrayList<Map<String,String>>();
        int tmp=0;
        try{
            while (rs.next()) {
                //rs.next();
                Map <String,String> data=new HashMap<String,String>();
                for (int i = 1; i <= rd.getColumnCount(); i++) {
                    data.put(rd.getColumnName(i), rs.getString(i));
                }
                several_row.add(data);
                tmp=tmp+1;
            }
        }catch (SQLException e){
            e.printStackTrace();
        }
        //Object r[] = new Object[1];
        //r[0] = data;
        //return r;
        //return data;
        return several_row;
    }

    public void remove() {

    }
    public static void main(String[] args) throws ClassNotFoundException,SQLException {
        String url_test="select * from Arts_AppRelation where AppName='distshop_child_score' or AppName='distnew_test'";
        //Iterator<Object[]> data_test=new DataProviderSQL(url_test,"128.7.7.32","3306","test","test","test");
        DataProviderSQL sql_test=new DataProviderSQL(url_test,"128.7.7.32","3306","test","test","test");
        List<Map<String,String>> severalrow_data=new ArrayList<Map<String,String>>();
        severalrow_data=sql_test.next();
        for (int i=0;i<severalrow_data.size();i++){
            Map<String,String> data=severalrow_data.get(i);
            for (Map.Entry<String, String> entry : data.entrySet()) {
                String k = entry.getKey();
                String v = entry.getValue();
                System.out.println( k + "   " + v + "  ");
            }
            System.out.println();
        }

    }
}
