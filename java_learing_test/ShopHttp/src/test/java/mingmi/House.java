package mingmi;

/**
 * Created by zhangmingmi on 16/8/17.
 */
public class House {
    private int area;
    private int price;


    public String sell(){
        return "House price is: " + area * price;
    }

    public int getArea() {
        return area;
    }

    public void setArea(int area) {
        this.area = area;
    }

    public int getPrice() {
        return price;
    }

    public void setPrice(int price) {
        this.price = price;
    }
}
