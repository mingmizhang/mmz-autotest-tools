package com.dp.mingmi.ShopHttp.BaseTest;

import com.dp.mingmi.ShopHttp.DataProviderSQL;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;


/**
 * Created by zhangmingmi on 16/8/16.
 */
public class SqlDataTest {
    private static Object[][] obj;

    public List<Map<String, String>> getsqldata(String sql,String ip,String port, String databasename, String user, String passwd) throws ClassNotFoundException, SQLException {
        //String url_test = "select * from Arts_AppRelation where AppName='distshop_child_score' or AppName='distnew_test'";
        //DataProviderSQL sql_test = new DataProviderSQL(url_test, "128.7.7.32", "3306", "test", "test", "test");
        DataProviderSQL sql_test = new DataProviderSQL(sql, ip, port, databasename, user, passwd);
        List<Map<String, String>> severalrow_data = new ArrayList<Map<String, String>>();
        severalrow_data = sql_test.next();
        return severalrow_data;
    }

    @Test(dataProvider = "sqlData")
    public void testsqldata(Map<String, String> s) {
        System.out.print("hello");
        for (Map.Entry<String, String> entry : s.entrySet()) {
            String k = entry.getKey();
            String v = entry.getValue();
            System.out.println(k + "   " + v + "  ");
        }

    }

    @DataProvider
    public Object[][] sqlData() throws SQLException, ClassNotFoundException {
        List<Map<String, String>> severalrow_data = getsqldata("select * from Arts_AppRelation where AppName='distshop_child_score' or AppName='distnew_test'", "128.7.7.32", "3306", "test", "test", "test");
        if (severalrow_data.size() > 0) {
            obj = new Object[severalrow_data.size()][];
            for (int i = 0; i < severalrow_data.size(); i++) {
                obj[i] = new Object[]{severalrow_data.get(i)};
            }
        }
        return obj;
    }

    @Test(dataProvider = "sqlDatastring")
    public void testsqldatastring(String testname, String appname, String appvalue) {
        System.out.print(testname);
        System.out.print(appname);
        System.out.print (appvalue);
        System.out.println();
        //Assert.assertTrue(value.equals("distshop_child_score"));
    }

    @DataProvider
    public Object[][] sqlDatastring() throws SQLException, ClassNotFoundException {
        List<Map<String, String>> severalrow_data = getsqldata("select * from Arts_AppRelation where AppName='distshop_child_score' or AppName='distnew_test'", "128.7.7.32", "3306", "test", "test", "test");
        if (severalrow_data.size() > 0) {
            obj = new Object[severalrow_data.size()][];
            for (int i = 0; i < severalrow_data.size(); i++) {
                Map<String, String> data = severalrow_data.get(i);
                for (Map.Entry<String, String> entry : severalrow_data.get(i).entrySet()) {
                    String k = entry.getKey();
                    String v = entry.getValue();
                    obj[i] = new Object[]{"test" + i, k, v};
                }
            }
        }
        return obj;
    }


}