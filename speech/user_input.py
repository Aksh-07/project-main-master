"""import cv2
import numpy as np
from PIL import Image
import os, time
import logging
import json
from datetime import datetime
"""
import logging
import android_actions as aa
import retail_actions as ra
from speech_errors import SpeechResult as enums
from speech_errors import SpeechProcessError, SpeechInvalidArgumentError
# from multiprocessing import Process, Lock, Value
from threading import Thread, RLock, Semaphore, enumerate
import queue
import numpy as np
import user_database
import python_wrapper
from py4j.java_gateway import JavaGateway, GatewayParameters

"""sample = [[1, 3, "some", 5], [0, 2, 4, 6], [0, 59, "thing", 2], [9, 5, "yes", 2], [9, 8, "Ko", 6]]
for x in sample:
    print(x)
print("--------------------")
sample.append([19, 18, "NUM", 16])
for x in sample:
    print(x)"""

android_actions = """ CREATE TABLE IF NOT EXISTS android_actions 
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL);"""

android_words = """ CREATE TABLE IF NOT EXISTS android_words
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL);"""

global_locations = """ CREATE TABLE IF NOT EXISTS global_locations
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL);"""

adverb_table = """ CREATE TABLE IF NOT EXISTS adverb_table
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL);"""

questions_tenses = """ CREATE TABLE IF NOT EXISTS questions_tenses
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL);"""

businesses = """ CREATE TABLE IF NOT EXISTS businesses
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category       TEXT     NOT NULL,
                                    Address        TEXT      NOT NULL,
                                    Updated_date   TEXT      NOT NULL);"""

business_supplies = """ CREATE TABLE IF NOT EXISTS business_supplies
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category      TEXT     NOT NULL,
                                    Brand         TEXT   NOT NULL,
                                    Updated_date  TEXT   NOT NULL);"""

business_actions = """ CREATE TABLE IF NOT EXISTS business_actions
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category      TEXT     NOT NULL,
                                    Brand         TEXT     NOT NULL,
                                    Updated_date  TEXT     NOT NULL);"""

available_supplies = """ CREATE TABLE IF NOT EXISTS available_supplies
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL,
                                    Brand         TEXT NOT NULL,
                                    Available_stores  TEXT   NOT NULL,
                                    Updated_date      TEXT   NOT NULL);"""

supply_add_ons = """ CREATE TABLE IF NOT EXISTS supply_add_ons
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL,
                                    Brand         TEXT    NOT NULL,
                                    Available_stores      TEXT  NOT NULL,
                                    Updated_date     TEXT   NOT NULL);"""

supply_descriptions = """ CREATE TABLE IF NOT EXISTS supply_descriptions
                                    (Size INT     NOT NULL,
                                    Matrix   TEXT    NOT NULL,
                                    Occurrence  INT      NOT NULL,
                                    Category            TEXT     NOT NULL,
                                    Brand         TEXT NOT NULL,
                                    Available_stores    TEXT NOT NULL,
                                    Updated_date    TEXT NOT NULL);"""

g_a_obj = None
g_r_obj = None

t_lock = RLock()

s_lock = Semaphore(3)
# m_lock2 = RLock()
# m_lock3 = Lock()

# text_threads = Value('i', 0)
# video_threads = Value('i', 0)
# audio_threads = Value('i', 0)

table_names = []
android_input_data = []
business_input_data = []
supplies_input_data = []
data_tag = []

# data_read = Value('i', 0)
# files_accessed = Value('i', 0)

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(format="%(levelname)s : %(message)s [%(module)s, %(funcName)s, %(lineno)d]", level=logging.DEBUG)
logging.getLogger("py4j").setLevel(logging.INFO)
g_db_obj = user_database.ProcessDataBaseRequests()


class BaseProcess():
    def __init__(self, name=None, target=None, args=()):
        super().__init__()
        self.args = args
        self.target = target
        self.thread_name = name

    def __del__(self):
        pass


class AudioProcess(BaseProcess):
    count = 2


class VideoProcess(BaseProcess):
    count = 3


class TextProcess(BaseProcess):
    count = 1


class ProcessUserInput:
    def __init__(self):
        """initiates self.py_wrapper_obj() abd stores it in self.g_py_obj
        """
        self.g_py_obj = self.py_wrapper_obj()

    def __del__(self):
        pass

    @staticmethod
    def py_wrapper_obj():
        """creates an object of PythonJavaBridge() class from python_wrapper module

        Returns:
            object: from class PythonJavaBridge()
        """
        logging.info("Success")
        return python_wrapper.PythonJavaBridge()

    @staticmethod
    def strings_to_matrix_calculation(str1: str):
        """takes the string and create a list containing size of each word in array form

        Args:
            str1 (str): string

        Returns:
            list: list with size of each word in string as an array
        """
        try:
            f, s = "", ""
            f_s, t_s, s_s, w0_s, w1_s, w2_s, w3_s = 0, 0, 0, 0, 0, 0, 0
            str_len = len(str1)
            w = [None] * 4
            i = 0
            if str_len > 1:
                f, s = str1[0:int(len(str1) // 2)], str1[int(len(str1) // 2):]
                if 1 < len(f) < 3:
                    f, w[0] = f[0:int(len(f) // 2)], f[int(len(f) // 2):]
                    i = i + 1
                elif int(len(f)) > 2:
                    f, w[i], w[i + 1] = f[0:int(len(f) // 3)], f[int(len(f) // 3): int(2 * len(f) // 3)], f[
                                                                                                          int(2 * (
                                                                                                                      len(f) //
                                                                                                                      3)):]
                    i = i + 2
                elif f and int(len(f)) == 1:
                    pass
                if 1 < int(len(s)) < 3:
                    s, w[i] = s[0:int(len(s) // 2)], s[int((len(s) // 2)):]
                    i = i + 1
                elif len(s) > 2:
                    s, w[i], w[i + 1] = s[0:int(len(s) // 3)], s[int(len(s) // 3): int(2 * len(s) // 3)], s[
                                                                                                          int(2 * (
                                                                                                                      len(s) //
                                                                                                                      3)):]
                    i = i + 2
                elif s and int(len(s)) == 1:
                    pass
            if str_len > 1:
                str1 = str1.encode('ascii')
                arr = np.frombuffer(str1, dtype=np.uint8)
                data_arr = np.array(arr)
                t_s = int(np.sum(data_arr))
                arr = np.frombuffer(f.encode('ascii'), dtype=np.uint8)
                data_arr = np.array(arr)
                f_s = int(np.sum(data_arr))
                arr = np.frombuffer(s.encode('ascii'), dtype=np.uint8)
                data_arr = np.array(arr)
                s_s = int(np.sum(data_arr))
                if w[0]:
                    arr = np.frombuffer(w[0].encode('ascii'), dtype=np.uint8)
                    data_arr = np.array(arr)
                    w0_s = int(np.sum(data_arr))
                if w[1]:
                    arr = np.frombuffer(w[1].encode('ascii'), dtype=np.uint8)
                    data_arr = np.array(arr)
                    w1_s = int(np.sum(data_arr))
                if w[2]:
                    arr = np.frombuffer(w[2].encode('ascii'), dtype=np.uint8)
                    data_arr = np.array(arr)
                    w2_s = int(np.sum(data_arr))
                if w[3]:
                    arr = np.frombuffer(w[3].encode('ascii'), dtype=np.uint8)
                    data_arr = np.array(arr)
                    w3_s = int(np.sum(data_arr))
            else:
                arr = np.frombuffer(str1.encode('ascii'), dtype=np.uint8)
                data_arr = np.array(arr)
                t_s = int(np.sum(data_arr))
            if str_len > 1 and w[0] is None and w[1] is None and w[2] is None and w[3] is None:
                word_lst = [t_s, str_len, [f_s, s_s]]
            elif str_len > 1 and w[0] is not None and w[1] is None and w[2] is None and w[3] is None:
                word_lst = [t_s, str_len, [f_s, s_s, w0_s]]
            elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is None and w[3] is None:
                word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s]]
            elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is not None and w[3] is None:
                word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s, w2_s]]
            elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is not None and w[3] is not None:
                word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s, w2_s, w3_s]]
            else:
                word_lst = [t_s, str_len]
            return word_lst
        except Exception as e:
            raise e

    def request_user_for_input(self, input_need):
        """calls request_user_input_from_java from python_wrapper module for additional input from user
        Raises:
            SpeechProcessError: _description_
        Returns:
            str: SUCCESS
            str: FAILURE
        """
        try:
            gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
            speech_process = gateway.jvm.speech.AppClass()
            que1 = queue.Queue()
            t1 = Thread(target=self.g_py_obj.request_user_input_from_java, args=(que1, input_need, speech_process,))
            t1.start()
            t1.join()
            second_input = que1.get()

            if second_input == enums.FAILURE.name:
                logging.error("No user input")
                return enums.FAILURE.name
            logging.info("Success")
            return second_input

        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def update_user_input_to_cloud(self, input_need: list):
        """calls update_new_words_to_analysis from python_wrapper module

        Args:
            input_need (list): missing input

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS
            str: FAILURE
        """
        try:
            gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
            speech_process = gateway.jvm.speech.AppClass()
            que2 = queue.Queue()
            t2 = Thread(target=self.g_py_obj.update_new_words_to_analysis, args=(input_need, que2, speech_process))
            t2.start()
            t2.join()
            if que2.get() == enums.FAILURE.name:
                logging.error("Failure")
                return enums.FAILURE.name
            logging.info("Success")
            return enums.SUCCESS.name
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechInvalidArgumentError(str(e))

    def start_audio_decode(self, data):
        pass

    def start_security_decode(self, data):
        pass

    def convert_strings_to_num_array(self, strings: str):
        """convert string entered by user to a list with items sum of each word, length of word, and word itself

        Args:
            strings (str): user entered string

        Raises:
            SpeechProcessError: _description_

        Returns:
            list: contains information about each word in string
            index: total length of string
        """
        try:

            strings = strings.lower()
            strings = strings.encode('utf_8')
            lst = strings.split()
            index = len(lst)
            words_lst = []
            for str1 in lst:
                arr = np.frombuffer(str1, dtype=np.uint8)
                data_arr = np.array(arr)
                matrix = self.strings_to_matrix_calculation(str1.decode("utf_8"))
                word_lst = [np.sum(data_arr).tolist(), matrix, str1]
                words_lst.append(word_lst)
            logging.info("Success")
            return words_lst, index
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def decode_user_input(self, _string: str):
        """convert user entered string into list contain each words information and then pass the information
        to decode_user_input_for_android_actions() and decode_user_input_for_retail_actions()
        of module android_action and retail_action simultaneously using threads
        for processing and give check the results 
        Args:
            _string (str): user entered string

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS
            str: INVALID_INPUT
        """
        try:
            gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
            speech_process = gateway.jvm.speech.AppClass()
            if _string is None:
                return enums.INVALID_INPUT.name
            else:
                words, index = self.convert_strings_to_num_array(_string)
            global g_a_obj, g_r_obj
            q_t = queue.Queue(2)
            g_a_obj = aa.AndroidActions(words)
            g_r_obj = ra.RetailActions(words)
            and_t = Thread(target=g_a_obj.decode_user_input_for_android_actions, args=(index, q_t, t_lock,),
                           daemon=True)
            ret_t = Thread(target=g_r_obj.decode_user_input_for_retail_actions, args=(index, q_t, t_lock,), daemon=True)
            and_t.start()
            ret_t.start()
            and_t.join()
            ret_t.join()
            ret_and = q_t.get()
            ret_ret = q_t.get()
            print(f"ret and: {ret_and}")
            print(f"ret ret: {ret_ret}")
            if ret_and != enums.SUCCESS.name:
                logging.debug("User intention is not a android action")
            elif ret_ret != enums.SUCCESS.name:
                logging.debug("User intention is not a retail action")
            if ret_and == enums.SUCCESS.name:
                logging.debug("User intention is a android action")
                t3 = Thread(target=self.g_py_obj.process_user_intention_actions,
                            args=(g_a_obj.generate_android_action_request(), speech_process,))
                t3.start()
                t3.join()
                # print("here")
                return enums.SUCCESS.name
            elif ret_ret == enums.SUCCESS.name:
                logging.debug("User intention is a retail action")
                t4 = Thread(target=self.g_py_obj.process_user_intention_actions,
                            args=(g_r_obj.generate_retail_action_request(), speech_process,))
                t4.start()
                t4.join()
                return enums.SUCCESS.name
            else:
                logging.error("Unable to process user input")
                for i in range(0, len(words)):
                    words[i][2] = words[i][2].decode("utf_8")
                # print(words)

                self.update_user_input_to_cloud(words)
                return enums.INVALID_INPUT.name
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def run(self, type_: str, _input: str):
        """Multiprocessing tasks based upon `type` and then process the user input `_input`

        Args:
            type_ (str): `audio`, `video` or `text`
            _input (str): user input

        Raises:
            SpeechInvalidArgumentError: _description_

        Returns:
            int: 1
            int: 0
        """
        try:
            if type_ == "audio":
                user_text = input("Enter something.\n")
                at = Thread(target=self.start_audio_decode, args=(user_text,), name="Audio")
                at.start()
                s_lock.acquire()
                # m_lock1.acquire()
                at.join()
                # m_lock1.release()
                s_lock.release()
                logging.info("Success")
                return 1
            elif type_ == "video":
                user_text = input("Enter something.\n")
                vt = Thread(target=self.start_security_decode, args=(user_text,), name="Video")
                vt.start()
                s_lock.acquire()
                # m_lock2.acquire()
                vt.join()
                # m_lock2.release()
                s_lock.release()
                logging.info("Success")
                return 1
            elif type_ == "text":
                tt = Thread(target=self.decode_user_input, args=(_input,), name="Text", daemon=True)
                tt.start()
                # m_lock3.acquire()
                s_lock.acquire()
                tt.join()
                # m_lock3.release()
                s_lock.release()
                logging.info("Success")
                return 1
            else:
                for p in enumerate():
                    p.join()
                logging.info("Success")
                return 0
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechInvalidArgumentError(str(e))


    def read_input_db_file(self, db_file: str):
        """read the .txt file given as parameter by user and update table_names, android_input_data, business_input_data, supplies_input_data, data_tag
        with suitable data

        Args:
            db_file (str): .txt file

        Raises:
            SpeechInvalidArgumentError: _description_

        Returns:
            list: table name
        """
        try:
            with open(db_file, 'r') as file1:
                lines = file1.read().splitlines()
                words_lst = []
                global table_names, android_input_data, business_input_data, supplies_input_data, data_tag
                for line in lines:
                    word_lst = line.split(",")
                    if word_lst[0] == "android":

                        data_tag.append(word_lst[0])
                        table_names.append(word_lst[1])
                        strings = word_lst[3].encode('utf_8')
                        arr = np.frombuffer(strings, dtype=np.uint8)
                        data_arr = np.array(arr)
                        words_lst.append(np.sum(data_arr).tolist())
                        # words_lst.append(data_arr.size)
                        matrix = self.strings_to_matrix_calculation(strings.decode("utf_8"))
                        words_lst.append(f"{matrix}")
                        occurrence = sum(x.count(np.sum(data_arr)) for x in android_input_data)
                        # occurrence1 = sum(x.count(np.sum(data_arr)) for x in android_input_data)
                        if occurrence == 0:
                            words_lst.append(1)
                        else:
                            words_lst.append(occurrence + 1)
                        # words_lst.append(strings)
                        words_lst.append(word_lst[4])

                        android_input_data.append(words_lst)
                        words_lst = []

                    elif word_lst[0] == "business":
                        data_tag.append(word_lst[0])
                        table_names.append(word_lst[1])
                        strings = word_lst[3].encode('utf_8')
                        arr = np.frombuffer(strings, dtype=np.uint8)
                        data_arr = np.array(arr)
                        words_lst.append(np.sum(data_arr).tolist())
                        # words_lst.append(data_arr.size)
                        matrix = self.strings_to_matrix_calculation(strings.decode("utf_8"))
                        words_lst.append(f"{matrix}")
                        occurrence = sum(x.count(np.sum(data_arr)) for x in business_input_data)
                        # occurrence1 = sum(x.count(np.sum(data_arr)) for x in business_input_data)
                        if occurrence == 0:
                            words_lst.append(1)
                        else:
                            words_lst.append(occurrence + 1)
                        # words_lst.append(strings)
                        words_lst.append(word_lst[4])
                        words_lst.append(word_lst[5])
                        words_lst.append(word_lst[6])
                        business_input_data.append(words_lst)
                        words_lst = []

                    elif word_lst[0] == "supplies":
                        data_tag.append(word_lst[0])
                        table_names.append(word_lst[1])
                        strings = word_lst[3].encode('utf_8')
                        arr = np.frombuffer(strings, dtype=np.uint8)
                        data_arr = np.array(arr)
                        words_lst.append(np.sum(data_arr).tolist())
                        # words_lst.append(data_arr.size)
                        matrix = self.strings_to_matrix_calculation(strings.decode("utf_8"))
                        words_lst.append(f"{matrix}")
                        occurrence = sum(x.count(np.sum(data_arr)) for x in supplies_input_data)
                        # occurrence1 = sum(x.count(np.sum(data_arr)) for x in supplies_input_data)
                        if occurrence == 0:
                            words_lst.append(1)
                        else:
                            words_lst.append(occurrence + 1)
                        # words_lst.append(strings)
                        words_lst.append(word_lst[4])
                        words_lst.append(word_lst[5])
                        words_lst.append(word_lst[6])
                        words_lst.append(word_lst[7])
                        supplies_input_data.append(words_lst)
                        words_lst = []
                    else:
                        logging.error("Invalid tag or line in db file")
                    word_lst.clear()
            logging.debug("Reading input db file success")
            return table_names
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechInvalidArgumentError(e)

    def update_local_data_base(self, db_file):
        """calls self.read_input_db_file() and insert rows in local created database with
        items stored in android_input_data, business_input_data, supplies_input_data
        depending on table_names and data_tag

        Args:
            db_file: .txt file to read data from

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: result from different insert functions from user_database module
        """
        try:
            g_db_obj.create_connection()
            global table_names, android_input_data, business_input_data, supplies_input_data, data_tag
            table_names.clear(), android_input_data.clear(),\
                business_input_data.clear(), supplies_input_data.clear(), data_tag.clear()
            if self.read_input_db_file(db_file) == enums.FATAL_ERROR.name:
                return enums.FATAL_ERROR.name
            res = enums.FAILURE.name
            a = 0
            b = 0
            s = 0
            for i, table in enumerate(table_names):
                if data_tag[i] == "android":
                    res = g_db_obj.insert_android_data(table, android_input_data[a])
                    if res != enums.SUCCESS.name:
                        logging.error("Failed to update android data at index {0} in table {1}".format(a, table))
                    else:
                        logging.info("Success")
                    a += 1
                elif data_tag[i] == "business":
                    res = g_db_obj.insert_business_supplies_data(table, business_input_data[b])
                    if res != enums.SUCCESS.name:
                        logging.error("Failed to update business data at index {0} in table {1}".format(b, table))
                    else:
                        logging.info("Success")
                    b += 1
                elif data_tag[i] == "supplies":
                    res = g_db_obj.insert_supplies_data(table, supplies_input_data[s])
                    if res != enums.SUCCESS.name:
                        logging.error("Failed to update supplies data at index {0} in table {1}".format(s, table))
                    else:
                        logging.info("Success")
                    s += 1
                else:
                    logging.error("Invalid data at index in table {0}".format(table))
            return res
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def delete_local_db_data(self, table_name: str, data_: str):
        """delete row from local database from given table_name by matching row with given data_

        Args:
            table_name (str): name of table
            data_ (str): data to delete from table

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: result from delete_db_data() from user_database module
        """
        try:
            g_db_obj.create_connection()
            keys, index = self.convert_strings_to_num_array(data_)
            res = enums.FAILURE.name
            for i in range(0, index):
                res = g_db_obj.delete_db_data(table_name, keys[i][0], keys[i][3])
                if res != enums.SUCCESS.name:
                    logging.error("Failed to delete data {0} from table {1}".format(keys[i][2], keys[i][0]))
            logging.info("Success")
            return res
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    @staticmethod
    def create_local_data_base(table_name: list):
        """calls create_table for each item in table_name after concerting the items to their values(sql query)

        Args:
            table_name (list): list of all the table names to be created

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: result from create_table() from user_database module
        """
        try:
            g_db_obj.create_connection()
            res = enums.FAILURE.name
            for table in table_name:
                res = g_db_obj.create_table(eval(table))
                if res != enums.SUCCESS.name:
                    logging.error("Failed to create table {}".format(table))
            logging.info("Success")
            return res
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))
