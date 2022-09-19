import logging

import user_database
import user_input
import android_actions
import retail_actions
import python_wrapper
import speech_errors
from time import time
import os
import numpy as np

table_names = []
android_input_data = []
business_input_data = []
supplies_input_data = []
data_tag = []


# def strings_to_matrix_calculation(str1):
#     try:
#         f, s = "", ""
#         f_s, t_s, s_s, w0_s, w1_s, w2_s, w3_s = 0, 0, 0, 0, 0, 0, 0
#         str_len = len(str1)
#         w = [None] * 4
#         i = 0
#         if str_len > 1:
#             f, s = str1[0:int(len(str1) // 2)], str1[int(len(str1) // 2):]
#             if 1 < len(f) < 3:
#                 f, w[0] = f[0:int(len(f) // 2)], f[int(len(f) // 2):]
#                 i = i + 1
#             elif int(len(f)) > 2:
#                 f, w[i], w[i + 1] = f[0:int(len(f) // 3)], f[int(len(f) // 3): int(2 * len(f) // 3)], f[
#                                                                                                       int(2 * (
#                                                                                                               len(f) //
#                                                                                                               3)):]
#                 i = i + 2
#             elif f and int(len(f)) == 1:
#                 pass
#             if 1 < int(len(s)) < 3:
#                 s, w[i] = s[0:int(len(s) // 2)], s[int((len(s) // 2)):]
#                 i = i + 1
#             elif len(s) > 2:
#                 s, w[i], w[i + 1] = s[0:int(len(s) // 3)], s[int(len(s) // 3): int(2 * len(s) // 3)], s[
#                                                                                                       int(2 * (
#                                                                                                               len(s) //
#                                                                                                               3)):]
#                 i = i + 2
#             elif s and int(len(s)) == 1:
#                 pass
#         if str_len > 1:
#             str1 = str1.encode('ascii')
#             arr = np.frombuffer(str1, dtype=np.uint8)
#             data_arr = np.array(arr)
#             t_s = int(np.sum(data_arr))

#             arr = np.frombuffer(f.encode('ascii'), dtype=np.uint8)
#             data_arr = np.array(arr)
#             f_s = int(np.sum(data_arr))
#             arr = np.frombuffer(s.encode('ascii'), dtype=np.uint8)
#             data_arr = np.array(arr)
#             s_s = int(np.sum(data_arr))
#             if w[0]:
#                 arr = np.frombuffer(w[0].encode('ascii'), dtype=np.uint8)
#                 data_arr = np.array(arr)
#                 w0_s = int(np.sum(data_arr))
#             if w[1]:
#                 arr = np.frombuffer(w[1].encode('ascii'), dtype=np.uint8)
#                 data_arr = np.array(arr)
#                 w1_s = int(np.sum(data_arr))
#             if w[2]:
#                 arr = np.frombuffer(w[2].encode('ascii'), dtype=np.uint8)
#                 data_arr = np.array(arr)
#                 w2_s = int(np.sum(data_arr))
#             if w[3]:
#                 arr = np.frombuffer(w[3].encode('ascii'), dtype=np.uint8)
#                 data_arr = np.array(arr)
#                 w3_s = int(np.sum(data_arr))
#         else:
#             arr = np.frombuffer(str1.encode('ascii'), dtype=np.uint8)
#             data_arr = np.array(arr)
#             t_s = int(np.sum(data_arr))
#         if str_len > 1 and w[0] is None and w[1] is None and w[2] is None and w[3] is None:
#             word_lst = [t_s, str_len, [f_s, s_s]]
#         elif str_len > 1 and w[0] is not None and w[1] is None and w[2] is None and w[3] is None:
#             word_lst = [t_s, str_len, [f_s, s_s, w0_s]]
#         elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is None and w[3] is None:
#             word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s]]
#         elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is not None and w[3] is None:
#             word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s, w2_s]]
#         elif str_len > 1 and w[0] is not None and w[1] is not None and w[2] is not None and w[3] is not None:
#             word_lst = [t_s, str_len, [f_s, s_s, w0_s, w1_s, w2_s, w3_s]]
#         else:
#             word_lst = [t_s, str_len]
#         return word_lst
#     except Exception as e:
#         raise e


# def read_input_db_file(db_file):
#     print("Prasad test")
#     try:
#         print("Prasad test-1")
#         with open(db_file, 'r') as file1:
#             lines = file1.read().splitlines()
#             print(lines)
#             words_lst = []
#             global table_names, android_input_data, business_input_data, supplies_input_data, data_tag
#             for line in lines:
#                 print("Prasad test-2")
#                 word_lst = line.split(",")
#                 print(word_lst)
#                 print("Prasad test-3")
#                 if word_lst[0] == "android":
#                     print("Prasad test-4")
#                     data_tag.append(word_lst[0])
#                     table_names.append(word_lst[1])
#                     strings = word_lst[3].encode('utf_8')
#                     arr = np.frombuffer(strings, dtype=np.uint8)
#                     data_arr = np.array(arr)
#                     words_lst.append(np.sum(data_arr).tolist())
#                     # words_lst.append(data_arr.size)
#                     matrix = strings_to_matrix_calculation(word_lst[3])
#                     words_lst.append(f"{matrix}")
#                     occurrence = sum(x.count(np.sum(data_arr)) for x in android_input_data)
#                     # occurrence1 = sum(x.count(np.sum(data_arr)) for x in android_input_data)
#                     if occurrence == 0:
#                         words_lst.append(1)
#                     else:
#                         words_lst.append(occurrence + 1)
#                     # words_lst.append(strings)
#                     words_lst.append(word_lst[4])

#                     android_input_data.append(words_lst)
#                     words_lst = []

#                 elif word_lst[0] == "business":
#                     print("Prasad test-4")
#                     data_tag.append(word_lst[0])
#                     table_names.append(word_lst[1])
#                     strings = word_lst[3].encode('utf_8')
#                     arr = np.frombuffer(strings, dtype=np.uint8)
#                     data_arr = np.array(arr)
#                     words_lst.append(np.sum(data_arr).tolist())
#                     # words_lst.append(data_arr.size)
#                     matrix = strings_to_matrix_calculation(word_lst[3])
#                     words_lst.append(f"{matrix}")
#                     occurrence = sum(x.count(np.sum(data_arr)) for x in business_input_data)
#                     # occurrence1 = sum(x.count(np.sum(data_arr)) for x in business_input_data)
#                     if occurrence == 0:
#                         words_lst.append(1)
#                     else:
#                         words_lst.append(occurrence + 1)
#                     # words_lst.append(strings)
#                     words_lst.append(word_lst[4])
#                     words_lst.append(word_lst[5])
#                     words_lst.append(word_lst[6])
#                     business_input_data.append(words_lst)
#                     words_lst = []

#                 elif word_lst[0] == "supplies":
#                     print("Prasad test-4")
#                     data_tag.append(word_lst[0])
#                     table_names.append(word_lst[1])
#                     strings = word_lst[3].encode('utf_8')
#                     arr = np.frombuffer(strings, dtype=np.uint8)
#                     data_arr = np.array(arr)
#                     words_lst.append(np.sum(data_arr).tolist())
#                     # words_lst.append(data_arr.size)
#                     matrix = strings_to_matrix_calculation(word_lst[3])
#                     words_lst.append(f"{matrix}")
#                     occurrence = sum(x.count(np.sum(data_arr)) for x in supplies_input_data)
#                     # occurrence1 = sum(x.count(np.sum(data_arr)) for x in supplies_input_data)
#                     if occurrence == 0:
#                         words_lst.append(1)
#                     else:
#                         words_lst.append(occurrence + 1)
#                     # words_lst.append(strings)
#                     words_lst.append(word_lst[4])
#                     words_lst.append(word_lst[5])
#                     words_lst.append(word_lst[6])
#                     words_lst.append(word_lst[7])
#                     supplies_input_data.append(words_lst)
#                     words_lst = []
#                 else:
#                     logging.error("Invalid tag or line in db file")
#                 word_lst.clear()
#         logging.debug("Reading input db file success")
#         return table_names
#     except Exception as e:
#         logging.error("{}".format(e))


# if __name__ == "__main__":
#     # start_time_ = time()
#     # if "user_tasks.db" not in os.listdir(
#     #         r"C:\Users\prasp\Videos\Captures\project-main-master\project-main-master\py4j"):
#     # read_input_db_file(r"C:\Users\kc\Downloads\project-main-master\project-main-master\py4j\data.txt")
#     # print(table_names)
#     obj = python_wrapper.PythonSpeechWrapper()
#     ui = user_input.ProcessUserInput()
#     ui.read_input_db_file(r"C:\Users\kc\Downloads\project-main-master\project-main-master\py4j\data.txt")
#     obj.create_local_db_tables(table_names=user_input.table_names)
#     user_input.table_names.clear(), user_input.android_input_data.clear(), user_input.business_input_data.clear(), user_input.supplies_input_data.clear(), user_input.data_tag.clear()

#     # obj.update_local_db("py4j/data.txt")
#     # r = user_database.ProcessDataBaseRequests()
#     # r.create_connection()
#     # rr = r.fetch_db_data("android_words", 752)
#     # print(rr)
#     # ui = obj.get_user_input("text")

#     # print(ui)
#     # dl = obj.delete_local_db_rows("supply_add_ons", "pizza")
#     # print("Total execution time : %s " %(time() - start_time_))


if __name__ == "__main__":
    print("start")
    start_time_ = time()
    user_obj = user_input.ProcessUserInput()
    obj = python_wrapper.PythonSpeechWrapper()

    if "user_tasks.db" not in os.listdir(r"C:\Users\kc\Downloads\project-main-master\project-main-master"):
        read_file = user_obj.read_input_db_file("py4j/data.txt")
        obj.create_local_db_tables(table_names=user_input.table_names)
        user_input.table_names.clear(), user_input.android_input_data.clear(),
        user_input.business_input_data.clear(), user_input.supplies_input_data.clear(), user_input.data_tag.clear()

    # obj.update_local_db("py4j/data.txt")
    # user_text = input("enter something\n")
    ui = obj.get_user_input("text")
    # print(ui)
    # dl = obj.delete_local_db_rows("supply_add_ons", "pizza")
    print("Total execution time : %s " %(time() - start_time_))
