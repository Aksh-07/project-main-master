import sqlite3
from sqlite3 import Error
from speech_errors import SpeechResult as enums
from speech_errors import SpeechProcessError
import logging
import requests

database = r"user_tasks.db"


class ProcessDataBaseRequests:
    def __init__(self):
        """initiate connection to database
        """
        self.conn = None

    def __del__(self):
        pass

    def create_connection(self):
        """if connection during initiation is none connect to the given database.

        Raises:
            SpeechProcessError: _description_
        """
        try:
            if self.conn is None:
                self.conn = sqlite3.connect(database, check_same_thread=False)
                logging.info("Success")
                return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def create_table(self, create_table_sql: str):
        """create table in database

        Args:
            create_table_sql (str): string to create table with all requirements

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if table is created
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            self.conn.commit()
            logging.info("Success")
            return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def delete_table(self, table_name: str):
        """Delete a table from database

        Args:
            table_name (str): name of table to delete

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if table deleted successfully
        """
        try:
            c = self.conn.cursor()
            q_str = "DROP TABLE {0}".format(table_name)
            c.execute(q_str)
            self.conn.commit()
            logging.info("Success")
            return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def insert_business_supplies_data(self, table_name: str, input_data: list):
        """to insert rows into tables related to business

        Args:
            table_name (str): name of table
            input_data (list): data to be inserted into rows

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if items are inserted into rows successfully
        """
        try:
            c = self.conn.cursor()
            q_str = "INSERT INTO {0} VALUES (?,?,?,?,?,?)".format(table_name)
            c.execute(q_str, input_data)
            self.conn.commit()
            logging.info("Success")
            return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def insert_supplies_data(self, table_name: str, input_data: list):
        """to insert rows into tables related to supplies

        Args:
            table_name (str): name of table
            input_data (list): data to be inserted into rows

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if items are inserted into rows successfully
        """
        try:
            c = self.conn.cursor()
            q_str = "INSERT INTO {0} VALUES (?,?,?,?,?,?,?)".format(table_name)
            c.execute(q_str, input_data)
            self.conn.commit()
            logging.info("Success")
            return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def insert_android_data(self, table_name: str, input_data: list):
        """to insert rows into tables related to android functions

        Args:
            table_name (str): name of table
            input_data (list): data to be inserted into rows

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if items are inserted into rows successfully
        """
        try:
            c = self.conn.cursor()
            q_str = "INSERT INTO {0} VALUES (?,?,?,?)".format(table_name)
            c.execute(q_str, input_data)
            self.conn.commit()
            logging.info("Success")
            return enums.SUCCESS.name
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def fetch_db_data(self, table_name: str, input_key: int):
        """fetch rows from given table_name where size matches input key

        Args:
            table_name (str): name of table
            input_key (int): size/weight of word to fetch

        Raises:
            SpeechProcessError: _description_

        Returns:
            list: table rows with matching items
        """
        try:
            c = self.conn.cursor()
            q_str = "SELECT * FROM {0} WHERE Size = ?".format(table_name)
            c.execute(q_str, (input_key,))
            records = c.fetchall()
            logging.info("Success")
            return records
        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def delete_db_data(self, table_name: str, input_key: int, input_data: bytes):
        """search for the row with matching input_key and input_data then delete the row if found.

        Args:
            table_name (str): name of table
            input_key (int): size/weight of word
            input_data (bytes): bytes string of word from convert_strings_to_num_array()

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if row is deleted
            str: DB_DELETE_ERROR if no matching row in database
        """
        try:
            records = self.fetch_db_data(table_name, input_key)
            # key_value = None
            if records is not None:
                # for row in records:
                #     if row[3] == input_data:
                #         key_value = row[3]
                parameters = {
                    "table name": table_name,
                    "size": records[0][0],
                    "occurrence": records[0][2],
                    "matrix": [r[1] for r in records],
                    "category": [r[3] for r in records],
                    "user_input_matrix": input_data
                }

                word_from_api = requests.get(url="", params=parameters)
                print(word_from_api.json())
                row_id = word_from_api
                c = self.conn.cursor()
                q_str = "DELETE FROM {0} WHERE rowid = ?".format(table_name)
                c.execute(q_str, (row_id,))
                self.conn.commit()
                logging.info("Success")
                return enums.SUCCESS.name
            else:
                logging.error("No matching row")
                return enums.DB_DELETE_ERROR.name

        except Error as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))
