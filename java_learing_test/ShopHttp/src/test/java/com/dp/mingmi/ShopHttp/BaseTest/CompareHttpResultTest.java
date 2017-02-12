package com.dp.mingmi.ShopHttp.BaseTest;

import com.dp.mingmi.ShopHttp.CompareHttpResult;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;


public class CompareHttpResultTest {
    private CompareHttpResult shopResult = new CompareHttpResult("http://******:4053/search/shop?query=term(cityid,1)","regionname","bizip");

    public Boolean at_least_one_shop_contains(String regionname,List<String> Record_List) throws IOException {
        Boolean Flag = false;
        for(int i = 0;i < Record_List.size();i++){
            if ((Record_List.get(i)).equals(regionname))
            {
                Flag = true;
                return Flag;
            }
        }
        return Flag;

    }

    @Test
    public void testShopOtherInfo() throws IOException {
        String Result = shopResult.GetResponseField();
        Assert.assertEquals(Result,"******:4053");
    }

    @Test
    public void testShopRecordInfo() throws IOException {
        List<String> Result= new ArrayList<String>();
        Result = shopResult.GetRecordField(shopResult.getRecord_field());
        boolean flag = at_least_one_shop_contains("音乐学院", Result);
        Assert.assertTrue(flag == false);
    }

    @Test(dataProvider = "testData")
    public void testShopRecorddataProvider(String testName,String regioname) throws IOException {
        System.out.println(testName);
        CompareHttpResult shopResult_Data = new CompareHttpResult("http://******:4053/search/shop?query=term(cityid,1),keyword(searchkeyword,%E5%B0%8F%E8%BE%89%E5%93%A5)","categoryname","bizip");
        List<String> Result= new ArrayList<String>();
        Result = shopResult_Data.GetRecordField(shopResult_Data.getRecord_field());
        boolean flag = at_least_one_shop_contains(regioname, Result);
        Assert.assertTrue(flag == true);
    }

    @DataProvider
    public Object[][] testData(){
        return new Object[][]{
                {"testCompare","全部"},
                {"testCompare","不是全部"}
        };
    }


}


