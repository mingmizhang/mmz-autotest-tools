package com.dp.mingmi.ShopHttp;

/**
 * Created by zhangmingmi on 16/8/16.
 */
public class ComputeHashcode {

    public static int value;

    public int hashCode(String s) {
        int h = 0;
        for (int i = 0; i < s.length(); ++i) {
            h = 31 * h + s.charAt(i);
        }
        return h;
    }

    public void compute() {
        int hashcodeValue= hashCode("abc");
        int modValue=(hashcodeValue % 4);
        value = modValue;
        System.out.print(hashcodeValue);
        System.out.println();
        System.out.println("the hashcode of the string which you input %4  is: ");
        System.out.print(modValue);
    }

    public static int hashCodeStatic(String s) {
        int h = 0;
        for (int i = 0; i < s.length(); ++i) {
            h = 31 * h + s.charAt(i);
        }
        return h;
    }

    public static void main(String[] args) {
        ComputeHashcode hashcode = new ComputeHashcode();
        hashcode.compute();
    }
}
