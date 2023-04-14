#!/usr/bin/env python

# Author: Github - nrkorte

import sys
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
import csv


dictionary_for_answers = {}


class bot:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=r"./chromedriver.exe")
        self.driver.set_window_position(2000, 0)
        self.driver.maximize_window()
        
    def start(self, user, passw, link):
        time.sleep(3)
        self.driver.get(link)
        try:
            WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'https://colostate.instructure.com/login/saml')]"))).click()
            WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user)
            WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(passw)
            WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@type, 'submit')]"))).click()
        except TimeoutException:
            print ("Error Code 0001: Unable to find elements relating to sign-in")
        time.sleep(1)

    def begin(self):
        get_into_quiz(self)

        self.driver.get(self.driver.current_url)

        try:
            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Question 1')]")))
            webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
        except TimeoutException:
            print ("Error Code 0001: Unable to locate element with the text \'Question 1\'\nExiting...")
            sys.exit()
        try:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-primary, .btn-secondary')))
        except TimeoutException:
            print ("Error Code 0001: Unable to find element with class name btn-secondary or btn-primary")
        count = 1
        while "btn-primary" not in element.get_attribute("class"):
            time.sleep(0.5)
            try:
                current_question = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//span[contains(text(), "Question {count}")]')))
                self.driver.execute_script("arguments[0].scrollIntoView();", current_question)
                count += 1
                parent = WebDriverWait(current_question, 3).until(EC.presence_of_element_located((By.XPATH, './parent::*/parent::*')))
                prompt_in_question = WebDriverWait(parent, 0.5).until(EC.presence_of_element_located((By.XPATH, './div[@class="text"]//*[contains(@class, "question_text")]'))).text

            except TimeoutException:
                print ("Error Code 0001: Unable to find element for creating prompt")
            if "multiple_choice_question" in parent.get_attribute("class") or "true_false_question" in parent.get_attribute("class"):
                solve_multiple_choice_question(self, dictionary_for_answers, prompt_in_question, parent)
            elif "short_answer_question" in parent.get_attribute("class"):
                solve_short_answer_question(self, dictionary_for_answers, prompt_in_question, parent)
            else:
                print ("Found a new question type! Submit a request at my github: https://github.com/nrkorte")

            # click submit button
            # remember to check current score at end of each attempt
            # keep this line at the bottom of the while loop
            try:
                element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-primary, .btn-secondary')))
            except TimeoutException:
                print ("Error Code 0001: Unable to find element with class name btn-secondary or btn-primary")
        finish()

def get_into_quiz(self):
    time.sleep(0.5)
    try:
        WebDriverWait( self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Take the Quiz')]"))).click()
    except TimeoutException:
        print ("Error Code 0001: Unable to locate \'Take the Quiz\'")
    try:
        WebDriverWait( self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Resume Quiz')]"))).click()
    except:
        print ("Error Code 0001: Unable to locate \'Resume Quiz\'\nExiting...")
        sys.exit()
            

def solve_multiple_choice_question(self, dictionary_, prompt_in_question, parent):
    count = 0
    for prompt in dictionary_:
        count += 1
        if prompt == prompt_in_question:
            answers = parent.find_elements(By.XPATH, './div[@class="text"]/div[@class="answers"]/fieldset/div[@class="answer"]')
            answers_text = []
            for y in answers:
                answers_text.append(y.text)

            for x in dictionary_.get(prompt):
                for i in range(len(answers_text)):
                    if str(x) == str(answers_text[i]):
                        xpath = answers[0].get_attribute("xpath")
                        for j in range(i):
                            xpath += "/following-sibling::div"
                        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath))).click()
    if count == len(dictionary_):
        count = 0
        try:
            answers = parent.find_elements(By.XPATH, './div[@class="text"]/div[@class="answers"]/fieldset/div[@class="answer"]')
            answers[0].click()
            answers_text = []
            for y in answers:
                answers_text.append(y.text)
        except TimeoutException:
            print ("Error Code 0001: Unable to find first choic in multiple choice question")

def solve_short_answer_question(self, dictionary_, prompt_in_question, parent):
    count = 0
    parent.click()
    webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
    try:
        answers = parent.find_elements(By.XPATH, './div[@class="text"]/div[@class="answers"]/*/*')
    except TimeoutException:
        print ("Error Code 0001: Unable to find element for answer placeholders")
    for prompt in dictionary_:
        count += 1
        if prompt == prompt_in_question:
            i = 0
            for x in dictionary_.get(prompt):
                try:
                    answers[i].send_keys(x)
                    i += 1
                    webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                except TimeoutException:
                    print ("Error Code 0001: Unable to find element for answer placeholder")
    if count == len(dictionary_):
        for i in range(len(answers)):
            try:
                answers[i].send_keys("test")
            except TimeoutException:
                print ("Error Code 0001: Unable to find element for answer placeholder")
            webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
        




def finish(tf): # parameter should be the bool for whether questions correct is equal to total questions
    save_dict()


def memory_dict():
    d = {}
    with open('mem.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            d.update({row[0]: row[1]})
    return d

def save_dict():
    try:
        with open('mem.csv', mode='w', newline='') as file:
            wrt = csv.writer(file, delimiter=",")
            for key, value in dictionary_for_answers.items():
                wrt.writerow[key, value]
    except:
        print ("Error code 0004: Unable to save current dictionary to mem.csv")

if __name__ == "__main__":
# arguments in order : username, password, link to hw
    if (len(sys.argv) != 4 and len(sys.argv) != 5):
        raise Exception("Error Code 0002: Wrong number of program arguments: found ", len(sys.argv) ," needed 3 additional. Exiting now...")
    if len(sys.argv) == 5:
        if sys.argv[4] == "mem":
            try:
                dictionary_for_answers = memory_dict()
            except:
                print ("Error Code 0003: Unable to load previous dictionary results")
        if sys.argv[4] == "del":
            save_dict()
    print ("Do not cancel out of this program before it hits submit or your answers may not be saved!\n")
    b = bot()
    b.start(sys.argv[1], sys.argv[2], sys.argv[3])
    b.begin()