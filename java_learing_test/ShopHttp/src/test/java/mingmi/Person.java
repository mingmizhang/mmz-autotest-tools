package mingmi;

/**
 * Created by zhangmingmi on 16/8/17.
 */
public class Person {

    public House house;
    public String name;
    public String address;

    public void sellHouse(){
        System.out.println("My name is:" + name);
        System.out.println("My address is:" + address);
        System.out.println("I am selling my house");
        System.out.println(getHouse().sell());
    }
    public void printall(){
        printname();
        printaddress();
    }
    public void printname(){
        System.out.print("My name is: " + name);
    }
    public void printaddress(){
        System.out.print("My address is: " + address);
    }



    public House getHouse() {
        return house;
    }

    public void setHouse(House house) {
        this.house = house;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }
}
