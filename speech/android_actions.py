from builtins import any as s_any
import logging
import queue

from numpy import array
from speech_errors import SpeechResult as enums
from speech_errors import SpeechProcessError
import user_database
import user_input

# import nlp_proc


# g_nlp_obj = nlp_proc.NLPProc()

# from decorators import status_check

query_type = ""
item_list = []
description = []
action_type = ""
location = "hillsboro"

g_db_obj = user_database.ProcessDataBaseRequests()


class AndroidActions:
    def __init__(self, text_input: array):
        """stores parameter text_input into self.data, creates an empty list with name self.words,
        initiates self.user_input_data_obj() with variable name self.g_ui_obj, and creates an object of
        user_database.creates_connection()

        Args:
            text_input (array): array from function convert_strings_to_num_array(strings)
        """
        self.data = text_input
        self.words = []
        self.g_ui_obj = self.user_input_data_obj()
        g_db_obj.create_connection()

    def __del__(self):
        pass

    @staticmethod
    def user_input_data_obj():
        """creates an object of ProcessUserInput() class from user_input module

        Returns:
            object: object of user_input.ProcessUserInput() class
        """
        logging.info("Success")
        return user_input.ProcessUserInput()

    def get_android_db_words(self, table: str, index: int):
        """Fetch all the rows from given table with the given index then find the one
        that match the user input and stores
        the string in self.words


        Args:
            table (str): table name to search and get data from.

            index (int): length of the array created by convert_strings_to_num_array(strings)

        Raises:
            SpeechProcessError: _description_

        Returns:
            bytes: r[3] if there is only one word in user input, 4th item of row is fetched from database
             which is a string converted into bytes.
            NONE: if there is no matching data found in database or there are more than one words in user input.
        """
        try:
            if index == 1:
                rows = g_db_obj.fetch_db_data(table, self.data[0][0])
                if rows:
                    # print(type(rows[0][0]))
                    # print(rows[0][0].decode())
                    occurrence = [r[2] for r in rows]
                    parameters = {
                        "table name": table,
                        "size": rows[0][0],
                        "occurrence": max(occurrence),
                        "matrix": [eval(r[1]) for r in rows],
                        "category": [r[3] for r in rows],
                        "user_input_matrix": self.data[0][1]
                    }
                    print(f"parameters 1: {parameters}")
                    res = None  # g_nlp_obj.nlp_proc_unit(parameters)
                    if res == -1:
                        return None
                    logging.info("Success")
                    return self.data[0][1]
                else:
                    # logging.debug("This is of intention to " + query_type + " android application")
                    logging.error(f"No match found in table: {table}")
                    return None
            else:
                for i in range(index):
                    rows = g_db_obj.fetch_db_data(table, self.data[i][0])
                    if rows:
                        parameters = {
                            "table name": table,
                            "size": rows[0][0],
                            "occurrence": rows[0][2],
                            "matrix": [r[1] for r in rows],
                            "category": [r[3] for r in rows],
                            "user_input_matrix": self.data[i][1]
                        }
                        print(f"parameters 2: {parameters}")

                        res = None  # g_nlp_obj.nlp_proc_unit(parameters)
                        if res == -1:
                            self.words.append(None)
                        self.words.append(self.data[i][1])
                        logging.info("Success")
                    else:
                        logging.debug(f"No matching data in table: {table}")
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def decode_user_input_for_android_actions(self, index, q_t, lock):
        """Decode and Process user input after getting an array and index from user_input.convert_strings_to_num_
        array(strings) and put results in queue q_t which can be either
        SUCCESS or INVALID_INPUT depending on conditions in the function.

        Args:
            index (int): length of the array created by convert_strings_to_num_array(strings)
            q_t (queue): object created from queue.Queue() class
            lock(lock): threading RLock object

        Raises:
            SpeechProcessError: _description_
        """
        try:
            lock.acquire()
            global query_type, action_type, location, item_list
            if index == 1 and self.get_android_actions(self.get_android_db_words("Android_actions",
                                                                                 index)):
                logging.debug("This is of intention to " + query_type + " android application")
                q_t.put(enums.SUCCESS.name, True)
            else:
                self.get_android_db_words("Android_words", index)
                if not self.words:
                    logging.error("No input user process")
                    q_t.put(enums.INVALID_INPUT.name)
                else:
                    word = self.words
                    if self.check_android_command_status(index) == enums.INSUFFICIENT_INPUT.name:
                        validate_word = self.validate_android_action()
                        if validate_word is not None:

                            words = self.g_ui_obj.request_user_for_input(validate_word)
                            if words is enums.FAILURE.name:
                                whole_input = [self.data[i][2] for i in range(index)]
                                insufficient_input = [x.decode("utf_8") for x in whole_input if x not in word]
                                logging.error("Insufficient user input, could not process '{}'".
                                              format(insufficient_input))
                                y = self.g_ui_obj.update_user_input_to_cloud(insufficient_input)
                                q_t.put(enums.INVALID_INPUT.name)
                                logging.info(y)
                            else:
                                self.words = []
                                query_type = ""
                                action_type = ""
                                item_list = []

                                # self.get_android_db_words("Android_words", index)
                                self.words = word
                                ni = self.additional_user_input(words)
                                if self.check_android_command_status(ni) == enums.INSUFFICIENT_INPUT.name:
                                    if self.validate_android_action() is not None:
                                        logging.error("Invalid input")
                                        q_t.put(enums.INVALID_INPUT.name)
                                    else:
                                        logging.info("Success")
                                        q_t.put(enums.SUCCESS.name)
                                else:
                                    if self.validate_android_action() is not None:
                                        logging.error("Invalid input")
                                        q_t.put(enums.INVALID_INPUT.name)
                                    else:
                                        logging.info("Success")
                                        q_t.put(enums.SUCCESS.name)
                        else:
                            logging.info("Success")
                            q_t.put(enums.SUCCESS.name)
                    else:
                        if self.validate_android_action() is not None:
                            logging.error("INVALID_INPUT")
                            q_t.put(enums.INVALID_INPUT.name)
                        else:
                            logging.info("Success")
                            q_t.put(enums.SUCCESS.name)
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))
        finally:
            lock.release()

    def check_android_command_status(self, index):
        """gets android action, intention, description and location to see if input is complete, insufficient or
         invalid as well as update query_type, action_type and item list, location, description depending on
         different conditions.

        Args:
            index (int): length of the array created by convert_strings_to_num_array(strings)

        Raises:
            SpeechProcessError: _description_

        Returns:
            SUCCESS: If everything works fine
            INSUFFICIENT_INPUT: if entered input misses some detail
            INVALID_ANDROID_ACTION_TYPE: If entered user input is not an android action
            SERVICE_NOT_AVAILABLE: if user entered input is weather
        """
        try:
            word_lst = self.words.copy()
            is_android_action = self.get_android_functions(word_lst)
            if is_android_action is not None:
                global query_type, action_type, location
                try:
                    word_lst.remove(is_android_action)
                except(ValueError, Exception):
                    is_android_action = str(is_android_action) + "s".encode('utf_8')
                    word_lst.remove(is_android_action)
                finally:
                    pass
                if not word_lst and is_android_action != "weather".encode('utf_8') and index == 1:
                    intention = "show"
                    query_type = intention
                    action_type = "android_action"
                    item_list.append(is_android_action.decode("utf_8"))
                    logging.debug("This is an " + action_type + " of intention to " + query_type + " " + item_list[0])
                    return enums.SUCCESS.name
                else:
                    intention = self.get_intention_type(is_android_action, index)
                    if intention is not None and intention.decode('utf_8') == "order":
                        if is_android_action.decode('utf_8') == "past" or is_android_action.decode(
                                'utf_8') == "history":
                            query_type = "show"
                            action_type = "android_action"
                            item_list.append(intention.decode('utf_8') + " " + "history")
                            logging.debug("This is an " + action_type + " of intention to " + query_type + " " +
                                          item_list[0])
                            return enums.SUCCESS.name
                        else:
                            logging.warning("May be " + is_android_action.decode('utf_8') + " is retailer action.")
                            return enums.INVALID_ANDROID_ACTION_TYPE.name
                    elif is_android_action.decode('utf_8') == "weather":
                        query_type = "show"
                        action_type = "android_action"
                        if self.get_location_for_weather_report(is_android_action, index) == enums.SUCCESS.name:
                            logging.debug("This is an " + action_type + " of intention to " + query_type + " " +
                                          item_list[0])
                            return enums.SERVICE_NOT_AVAILABLE.name
                        return enums.SUCCESS.name
                    elif intention is not None:
                        query_type = intention.decode('utf_8')
                        action_type = "android_action"
                        item_list.append(is_android_action.decode("utf_8"))
                        if self.check_android_description_need:
                            d = self.get_android_description(query_type, item_list)
                            if d == enums.SUCCESS.name:
                                logging.debug("This is an " + action_type + " of intention to " + query_type + " " +
                                              item_list[0] + " " + description[0])
                                return enums.SUCCESS.name
                            else:
                                logging.error("Insufficient input")
                                return enums.INSUFFICIENT_INPUT.name
                        else:
                            logging.debug("This is an " + action_type + " of intention to " + query_type + " " +
                                          item_list[0])
                            return enums.SUCCESS.name
                    else:
                        item_list.append(is_android_action.decode("utf_8"))
                        action_type = "android_action"
                        logging.error("Insufficient input")
                        return enums.INSUFFICIENT_INPUT.name
            else:
                logging.error("This is not a android action")
                return enums.INVALID_ANDROID_ACTION_TYPE.name
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def get_android_functions(self, words: bytes):
        """get android_action by matching for any word in argument words present in self.data.

        Args:
            words (bytes): items in self.words after running get_android_db_words()

        Raises:
            SpeechProcessError: _description_

        Returns:
            bytes: string converted into bytes which is 3rd item in self.data
            NONE: if function condition does not work
        """
        try:
            for word in self.data:
                if s_any(word[2] in s for s in words):
                    logging.info("Success")
                    return word[2]
            logging.error("return None")
            return None
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def get_android_actions(self, words: bytes):
        """put item in query type if words match byte string in self.words

        Args:
            words (bytes): returned value from get_android_db_words()

        Raises:
            SpeechProcessError: _description_

        Returns:
            NONE: if words == order or NONE
            words: if words == byte string stored in self.data
        """
        try:
            if "order".encode("utf_8") == words or words is None:
                logging.info("return None")
                return None
            if words == self.data[0][2]:
                global query_type
                query_type = words.decode('utf_8')
                logging.info("Success")
                return words
            else:
                logging.error("return None")
                return None
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def get_location_for_weather_report(self, words: bytes, index: int):
        """search global locations table for location name to get weather report

        Args:
            words (bytes): is_android_action
            index (int): length of the array created by convert_strings_to_num_array(strings)

        Raises:
            SpeechProcessError: _description_

        Returns:
            str: SUCCESS if current location is given or location is present in database
            str: INVALID_LOCATION if location is not present in database
        """
        try:
            global location
            current_location = location
            self.get_android_db_words("Global_locations", index)
            weather_location = self.words.copy()
            weather_location.remove(words)
            if index == 1:
                item_list.append(current_location + " " + "weather")
                logging.info("Success")
                return enums.SUCCESS.name
            elif not weather_location:
                logging.error("The location you are interested is not under countries we provide our services")
                return enums.INVALID_LOCATION.name
            else:
                location = weather_location[0]
                item_list.append(location.decode('utf_8') + " " + "weather")
                logging.info("Success")
                return enums.SUCCESS.name
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    def get_intention_type(self, words: bytes, index: int):
        """get intention by checking for any matching word in argument words with words from table android actions

        Args:
            words (bytes): is_android_action
            index (int): length of the array created by convert_strings_to_num_array(strings)

        Raises:
            SpeechProcessError: _description_

        Returns:
            bytes: byte string word if any match
            NONE: if no match
        """
        try:
            self.get_android_db_words("Android_actions", index)
            action_list = self.words.copy()
            action_list.remove(words)
            for word in action_list:
                if s_any(word in s for s in self.data):
                    logging.info("Success")
                    return word
            logging.error("return None")
            return None
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    @staticmethod
    def generate_android_action_request():
        """creates a list of dictionaries with keys `query_type`, `item_list`, `description`, `action_type`
        and its corresponding values

        Returns:
            list: a list of dictionaries items with key value pairs
        """
        lis = [{"query_type": query_type}, {"item_list": item_list},
               {"description": description}, {"action_type": action_type}]
        logging.info("Success")
        return lis

    def validate_android_action(self):
        """validate android action by checking required details like action_type, query_type,
        item_list, description values

        Raises:
            SpeechProcessError: _description_

        Returns:
            NONE: if word list is NONE
            word: a list with missing details
        """
        try:
            word = []
            if not action_type:
                logging.error("Android android_type is not available")
                word.append("android_action")
            if not query_type:
                logging.error("Android query type is not available")
                word.append("query_type")
            if not item_list:
                logging.error("Android item list is not available")
                word.append("item_list")
            if not description and self.check_android_description_need():
                logging.error("Android description is not available")
                word.append("description")
            if not word:
                logging.info("Success return none")
                return None
            else:
                logging.error(f"insufficient input require {word}")
                return word
        except Exception as e:
            logging.error(f"{e}")
            raise SpeechProcessError(str(e))

    @staticmethod
    def check_android_description_need():
        """check for if description is required

        Returns:
            boolean: True or FALSE depending on conditions
        """
        if "photos" in item_list or "music" in item_list or "videos" in item_list:
            logging.info("return True")
            return True
        elif query_type == "play":
            logging.info("return True")
            return True
        else:
            logging.info("return False")
            return False

    def additional_user_input(self, user_text: str):
        """get input from java side and updates self.data with new data and return updated index

        Args:
            user_text (str): user input from java

        Returns:
            int: updated index
        """
        new_word, new_index = self.g_ui_obj.convert_strings_to_num_array(user_text)
        self.data = new_word
        logging.info("Success")
        return new_index

    def get_android_description(self, query: str, item: list):
        """check for description from self.data

        Args:
            query (str): query_type
            item (list): item_list

        Returns:
            str: SUCCESS
            str: FAILURE
        """
        words = []
        for i in range(len(self.data)):
            words.append(self.data[i][2])
        words = [w.decode("utf_8") for w in words]
        words.remove(query)
        print(f"item: {item}")
        for a in item:
            words.remove(a)
        if words:
            for item in words:
                description.append(item)
                logging.info("Success")
            return enums.SUCCESS.name
        else:
            logging.error("Failure")
            return enums.FAILURE.name
