package speech;


public interface PythonObject
{
    public String get_user_input(String type, String input);
    public String update_local_db(String dbFileString);
    public String create_local_db_tables(String dbFileString);
    public String delete_local_db_rows(String table_name, String data);
}
