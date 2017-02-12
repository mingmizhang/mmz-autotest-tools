package com.dp.mingmi.ShopHttp.BaseTest;

import com.dp.mingmi.ShopHttp.CompareHttpResult;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;


public class SeparateDataTest{
    @Test(dataProvider = "testData",groups = {"p2"})
    public void dataseparatetest  (String testname,String url,String record_test,String otherinfo_test,String validate_value) throws IOException {
        CompareHttpResult shopResult = new CompareHttpResult(url,record_test,otherinfo_test);
        System.out.println(testname);
        List<String> Result= new ArrayList<String>();
        Result = shopResult.GetRecordField(shopResult.getRecord_field());
        CompareHttpResultTest shopResultTest = new CompareHttpResultTest();
        //boolean flag = shopResultTest.at_least_one_shop_contains("海底捞火锅", Result);
        boolean flag = shopResultTest.at_least_one_shop_contains(validate_value, Result);
        Assert.assertTrue(flag == true);
    }
    @DataProvider
    public Object[][] testData(){
        return new Object[][]{
                {"Separatetest1","http://******:4053/search/shop?query=keyword(searchkeyword,%E6%B5%B7%E5%BA%95%E6%8D%9E)&fl=shopname","shopname","bizip","海底捞火锅"},
                {"Separatetest2","http://******:4053/search/shop?query=term(shopid,22188562)&fl=shopname","shopname","bizip","海底捞火锅"}
        };
    }
}