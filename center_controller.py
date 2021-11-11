# author: sanqiushu
# date: 2021/11/10
import threading
from queue import Queue
import time
import importlib
from concurrent.futures import ThreadPoolExecutor
import sys


class CenterController:
    # 1 还没开始写，2 正在写 3 写完了
    INPUT_STATUS = 1
    # 1 还没开始验证，2 正在验证 3 验证完了
    POC_SCAN_STATUS = 1
    # 1 还没开始输出，2 正在输出 3 输出完了
    OUTPUT_STATUS = 1
    # 1 程序开始 2 程序结束
    RUN_STATUS = 1
    # 看一下有多少个目标要测试
    target_len = 0

    target_queue = Queue(1000)
    result_queue = Queue(1000)

    # 读文件，然后加入到 队列里
    def start_target_input(self):
        # print(time.time(),"开始写入目标列表")
        # 开始进行目标输入
        self.INPUT_STATUS = 2
        # 打开目标文件
        target_file = open('target.txt')
        # 把目标都读进来
        target_list = target_file.readlines()
        # 计算一下有多少
        self.target_len = target_len = len(target_list)
        # 设置一个标志位，用来判读有多少目标已经写到队列里面了，后面可以用 pop() 函数代替
        flag = 0
        while True:
            # 如果队列不是空的话
            if not self.target_queue.full():
                # 往里加目标
                self.target_queue.put(target_list[flag].replace("\n", ''))
                flag += 1
            # 如果队列满了
            else:
                # 先等等
                time.sleep(0.1)
            if flag >= target_len:
                break
        self.INPUT_STATUS = 3  # 目标输入结束
        # print("完成目标写入")
        # print(time.time(), "完成目标写入")

    # 基本逻辑就是，创建 N 个线程，然后让线程跑去吧
    def start_poc_check(self):
        # print(time.time(), "开始poc验证")
        # 标识开始poc测试
        self.POC_SCAN_STATUS = 2
        # 加载 poc.py文件
        poc = importlib.import_module('poc')
        # 创建一个 10 个线程的线程池
        pool = ThreadPoolExecutor(max_workers=10)
        # 建立 10 个线程
        th_list = []
        for i in range(10):
            # 让他们去跑 poc文件的poc函数去吧, 函数参数传递要注意点，别写错了
            th = threading.Thread(target=poc.poc, args=(self.target_queue, self.result_queue))
            th.setDaemon(True)
            th.start()
            th_list.append(th)
        # print(time.time(), "10个线程创建完成")
        while True:
            # 如果目标 队列空了，而且输入还结束了，那就说明结束了啊
            if self.target_queue.empty() and self.INPUT_STATUS == 3:
                break
            else:
                # 如果程序没结束呢，先等等再继续
                time.sleep(0.5)
            # 设置一个标志位
            th_flag = -1
            # 循环判断是不是有的线程挂掉了
            for i in range(10):
                if not th_list[i].is_alive():
                    th_flag = i
                    print("线程挂了", th_flag)
            # 如果那个线程挂了 ，从新起来一个
            th_list.pop(th_flag)
            th = threading.Thread(target=poc.poc, args=(self.target_queue, self.result_queue))
            th.setDaemon(True)
            th.start()
            th_list.append(th)
            time.sleep(0.5)
        self.POC_SCAN_STATUS = 3  # 验证结束了
        # print("完成poc验证")
        # print(time.time(), "完成poc验证")

    def start_result_output(self):
        # print(time.time(), "开始输出")
        flag = 0
        while True:
            if self.result_queue.empty():
                time.sleep(1)
            else:
                result = self.result_queue.get()
                flag += 1
                show_line = "正在验证：【 " + str((flag / self.target_len) * 100)[:4] + "%" +" 】" + \
                            "【 " + result['is_vuln'] + " 】" + result['target']

                print(show_line)
            # 如果验证结束了 且 输出的数量够的
            if self.POC_SCAN_STATUS == 3 and flag == self.target_len:
                break
        self.OUTPUT_STATUS = 3
        self.RUN_STATUS = 2
        # print("完成结果输出")
        # print(time.time(), "完成结果输出")

    def cent_core(self):
        # 这三个都是开启后就不用管了
        threading.Thread(target=self.start_target_input).start()
        threading.Thread(target=self.start_poc_check).start()
        threading.Thread(target=self.start_result_output).start()
        while True:
            if self.RUN_STATUS == 2:
                break
        # print("验证完成，程序退出")
        exit("全部结束")

    def run(self):
        self.cent_core()
        pass

    pass


a = CenterController()
a.run()
