package speech;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.logging.*;
import py4j.ClientServer;
import java.util.ArrayList;

class MyThread1 extends Thread {
    /*creates a thread from function sendToPython of class AppClass */
    public MyThread1(String name) {
        super(name);

    }

    @Override
    public void run() {
        System.out.println("Thread 1 is running");
        try {
            AppClass.sendToPython();
        } catch (Exception e) {
            System.out.println(e);
        }

    }
}

public class AppClass {
    static String first_input;
    static String javaContinue;
    static ClientServer clientServer;
    static Logger logger = Logger.getLogger(AppClass.class.getName());

    public String fillDataForSpeechRequest(ArrayList<Object> a) throws IOException {
        /*ask for input from user if first input is insufficient
         * return string as Success or Failure
         */
        try {
        InputStreamReader r = new InputStreamReader(System.in);
        BufferedReader br = new BufferedReader(r);
        String string = String.format("Insufficient input. Missing %s\nEnter input again : ", a);
        System.out.print(string);
        String str = br.readLine();
        logger.log(Level.INFO, "Success");
        return str;
        } catch (Exception e) {
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
        

    }

    public static String enterFirstInput() throws IOException {
        /*get first input from java to send to python for processing
         * return string as Success or Failure
         */
        try {
        InputStreamReader r = new InputStreamReader(System.in);
        BufferedReader br = new BufferedReader(r);
        System.out.print("Enter input :");
        first_input = br.readLine();
        logger.log(Level.INFO, "Success");
        return "Success";
        } catch (Exception e) {
        System.out.println(e);
        logger.log(Level.INFO, "Failure");
        return "Failure";
        }

        
    }

    public static String updateNewWordsCloud(ArrayList<Object> b) {
        /*print list of word and its information that is recieved from python
         * return string as Success or Failure
         */
        try {
        System.out.println(b);
        logger.log(Level.INFO, "Success");
        return "Success";
        } catch (Exception e) {
        System.out.println(e);
        logger.log(Level.INFO, "Failure");
        return "Failure";
        }
        
    }

    public String processUserActions(ArrayList<Object> c) {
        /*print list containg all the information after processing is done by python 
         * return string as Success or Failure
         */
        try {
            System.out.println(c);
            logger.log(Level.INFO, "Success");
            return "Success";
        } catch (Exception e) {
            System.out.println(e);
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
        
    }

    public static String startGatewayServer() {
        /*start java gateway server to let python call java functions
         * return string as Success or Failure
         */
        try {
        AppClass y = new AppClass();
        clientServer = new ClientServer(y);
        clientServer.startServer();
        System.out.println("Java servere started");
        logger.log(Level.INFO, "Success");
        return "Success";
        } catch (Exception e) {
        System.out.println(e);
        logger.log(Level.INFO, "Failure");
        return "Failure";
        }
        
    }

    public static String sendToPython() throws IOException {
        /*Create a call back server to acess python class and call get_user_input() from python_wrapper with the input from java as parameter
         * return string as Success or Failure
          */
        try {
            PythonObject pyObject = (PythonObject) ((ClientServer) clientServer)
                .getPythonServerEntryPoint(new Class[] { PythonObject.class });
        javaContinue = "y";
        while (javaContinue.equals("y")) {
            enterFirstInput();
            pyObject.get_user_input("text", first_input);

            InputStreamReader r = new InputStreamReader(System.in);
            BufferedReader br = new BufferedReader(r);
            System.out.print("Enter s to stop, y to continue.\n");
            javaContinue = br.readLine();

            if (!javaContinue.equals("y")) {
                ((ClientServer) clientServer).shutdown();
                System.out.println("Java gateway closed");
            }
        }
            logger.log(Level.INFO, "Success");
            return "Success";
        } catch (Exception e) {
            System.out.println(e);
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
        
    }

    public static String createLocalDb(){
        /*Create a call back server to acess python class and call create_local_db_tables from python_wrapper
         * return string as Success or Failure
         */
        try {
            InputStreamReader r1 = new InputStreamReader(System.in);
            BufferedReader br1 = new BufferedReader(r1);
            System.out.print("Enter db file location.\n");
            String dbFile = br1.readLine();

            PythonObject pyObject = (PythonObject) ((ClientServer) clientServer)
                .getPythonServerEntryPoint(new Class[] { PythonObject.class });

            pyObject.create_local_db_tables(dbFile);
            logger.log(Level.INFO, "Success");
            return "Success";
        } catch (Exception e) {
            System.out.println(e);
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
    }

    public static String updateLocalDb(){
        /*Create a call back server to acess python class and call update_local_db from python_wrapper
         * return string as Success or Failure
         */
        try {
            InputStreamReader r1 = new InputStreamReader(System.in);
            BufferedReader br1 = new BufferedReader(r1);
            System.out.print("Enter db file location.\n");
            String dbFile = br1.readLine();

            PythonObject pyObject = (PythonObject) ((ClientServer) clientServer)
                .getPythonServerEntryPoint(new Class[] { PythonObject.class });

            pyObject.update_local_db(dbFile);
            logger.log(Level.INFO, "Success");
            return "Success";
        } catch (Exception e) {
            System.out.println(e);
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
    }

    public static String deleteLocalDb(){
        /*Create a call back server to acess python class and call delete_local_db_rows from python_wrapper
         * return string as Success or Failure
         */
        try {
            InputStreamReader r1 = new InputStreamReader(System.in);
            BufferedReader br1 = new BufferedReader(r1);
            System.out.print("Enter table name.\n");
            String tableName = br1.readLine();

            InputStreamReader r2 = new InputStreamReader(System.in);
            BufferedReader br2 = new BufferedReader(r2);
            System.out.print("Enter data to delete.\n");
            String data = br2.readLine();

            PythonObject pyObject = (PythonObject) ((ClientServer) clientServer)
                .getPythonServerEntryPoint(new Class[] { PythonObject.class });

            logger.log(Level.INFO, "Success");
            pyObject.delete_local_db_rows(tableName, data);
            return "Success";
        } catch (Exception e) {
            System.out.println(e);
            logger.log(Level.INFO, "Failure");
            return "Failure";
        }
    }

    public static void main(String[] args) throws IOException {

        startGatewayServer();
        // createLocalDb();
        // updateLocalDb();
        // sendToPython();
        MyThread1 t1 = new MyThread1("first");
        t1.start();

    }

}
