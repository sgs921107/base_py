#!/usr/bin/env python
# -*- coding=utf8 -*-
import re
import os
import json
import subprocess
from dotenv.main import DotEnv


class EnvManage(object):

    def __init__(self, env_path):
        if os.path.isfile(env_path) is False:
            raise ValueError("env path '%s' is not a file" % env_path)
        self.env_path = env_path
        self.envs = self.read_envs()
        blank_line_regex = r"^\s*$"
        annotation_line_regex = r"^#\s[^\[]*$"
        self.blank_line_regexp = re.compile(blank_line_regex)
        self.annotation_line_regexp = re.compile(annotation_line_regex)

    def read_envs(self):
        manager = DotEnv(self.env_path)
        envs = manager.dict()
        return envs

    def show_sections(self):
        sections = set()
        for env in self.envs:
            section = env.split("_")[0]
            sections.add(section)
        sections = list(sections)
        print(json.dumps(sections, ensure_ascii=False, indent=4))
        return sections

    def show_envs(self, indent=4):
        data = json.dumps(self.envs, ensure_ascii=False, indent=indent)
        print(data)
        return self.envs

    def search_envs(self, keyword, indent=4):
        """
        检索以关键词开头的env
        :param keyword: 关键词
        :param indent: json序列化时的缩进参数
        :return: 包含关键词的配置项
        """
        result = dict()
        for key, val in self.envs.items():
            if key.startswith(keyword):
                result[key] = val
        data = json.dumps(result, ensure_ascii=False, indent=indent)
        print(data)
        return result

    def search_env(self, name):
        value = self.envs.get(name)
        if value is None:
            print("env文件中未包含配置项：%s" % name)
        else:
            print("%s的当前值为: '%s'" % (name, value))
        return value

    def add_section(self, section, check=True):
        """
        追加板块
        :param section: 板块
        :param check: 追加验证是否已存在
        :return: bool
        """
        if check is True:
            print("start check section %s is exist" % section)
            line_no = self.has_section(section)
            if line_no:
                print("add section failed: section %s already exist" % section)
                return False
        end_line = subprocess.getoutput('tail -1 %s' % self.env_path)
        print("start add section %s" % section)
        # 如果文件结尾非空行,则先追加一个空行
        if not self.blank_line_regexp.match(end_line):
            cmd = 'echo "" >> %s' % self.env_path
            subprocess.call(cmd, shell=True)
        cmd = 'echo "# [%s]" >> %s' % (section, self.env_path)
        subprocess.call(cmd, shell=True)
        line_no = self.has_section(section)
        if line_no is False:
            print("add section %s failed" % section)
            return False
        else:
            print("add section %s succeed" % section)
            return True

    def has_section(self, section):
        """
        检查是否存在指定板块
        :param section: 板块
        :return: bool
        """
        cmd = r'sed -n "/^# \[%s\]/=" %s' % (section, self.env_path)
        line_no = subprocess.getoutput(cmd)
        if line_no == "":
            print("section %s not found" % section)
            return False
        print("section %s on the line: %s" % (section, line_no))
        return line_no

    def del_section(self, section):
        """
        删除板块及板块下的所有env
        :param section: 板块名
        :return:
        """
        exist = self.has_section(section)
        if exist is False:
            print("del section failed: section %s not found" % section)
            return False
        # section所在的行
        lines = [int(line) for line in exist.split()]
        # 删除section上面的空行
        for line in lines:
            # 是在第一行则跳过
            if line == 1:
                continue
            pre_line = line - 1
            # 查看上一行的内容
            pre_line_content_cmd = "sed -n '%dp' %s" % (pre_line, self.env_path)
            pre_line_content = subprocess.getoutput(pre_line_content_cmd)
            # 如果上一行不为空则跳过
            if not self.blank_line_regexp.match(pre_line_content):
                continue
            # 删除上面的空行
            del_pre_line_cmd = "sed -i '%dd' %s" % (pre_line, self.env_path)
            subprocess.call(del_pre_line_cmd, shell=True)
        cmd = r'sed -i "/^# \[%s\]/d" %s' % (section, self.env_path)
        subprocess.call(cmd, shell=True)
        exist = self.has_section(section)
        if exist is False:
            print("del section %s succeed" % section)
            print("start del envs about the section %s" % section)
            envs = self.search_envs(section)
            for env in envs:
                self.del_env(env)
            return True
        else:
            print("del section %s failed" % section)
            return False

    def del_env(self, name):
        """
        删除一个env
        :param name: 要删除的env名
        :return:
        """
        exist = self.search_env(name)
        if exist is None:
            print("del env failed: env %s not found" % name)
            return False
        line_cmd = 'sed -n "/^%s=/=" %s' % (name, self.env_path)
        line = int(subprocess.getoutput(line_cmd))
        pre_line = line - 1
        # 查看上一行的内容
        pre_line_content_cmd = "sed -n '%dp' %s" % (pre_line, self.env_path)
        pre_line_content = subprocess.getoutput(pre_line_content_cmd)
        # 如果上面一行时注释, 则删除注释
        if self.annotation_line_regexp.match(pre_line_content):
            del_pre_line_cmd = "sed -i '%dd' %s" % (pre_line, self.env_path)
            subprocess.call(del_pre_line_cmd, shell=True)
        # 删除配置行
        cmd = 'sed -i "/^%s=/d" %s' % (name, self.env_path)
        subprocess.call(cmd, shell=True)
        # 判断是否删除成功
        new_envs = self.read_envs()
        value = new_envs.get(name)
        if value is None:
            print("del env %s succeed" % name)
            return True
        else:
            print("del env %s failed, the value is '%s'" % (name, value))
            return False

    def add_env(self, section, name, value):
        """
        追加一个env
        :param section: 指定追加到哪个部分下面
        :param name: 要追加的变量名
        :param value: 变量的值
        :return: 是否更改成功 -> bool
        """
        if name == "" or section == "":
            print("add env failed: param name and section can't is ''")
            return False
        name = "_".join([section, name])
        # 判断env是否已存在
        exist = self.search_env(name)
        # 如果已存在则进行更新
        if exist is not None:
            print("env %s is already exist, will be updated" % name)
            return self.update_env(name, value)
        line_no = self.has_section(section)
        # 如果板块不存在则追加板块
        if line_no is False:
            self.add_section(section, check=False)
        # 追加env到板块下的命令
        cmd = r'sed -i "/^# \[%s\]/a%s=%s" %s' % (section, name, value, self.env_path)
        # 执行追加命令
        subprocess.call(cmd, shell=True)
        # 判断是否追加成功
        new_envs = self.read_envs()
        value = new_envs.get(name)
        if value is not None:
            print("add env %s succeed, value is '%s'" % (name, value))
            return True
        else:
            print("add env %s failed" % name)
            return False

    def update_env(self, name, value):
        """
        更新配置
        :param name: 要更新的配置项
        :param value: 新值
        :return: 是否更改成功 -> bool
        """
        ret = False
        exist = self.search_env(name)
        if exist is None:
            print("修改失败, 该方法不支持新增配置项")
        elif exist == value:
            print("不需要修改,配置项%s要修改的值%s跟原来的值%s是一致的" % (name, value, exist))
        else:
            print("开始修改配置")
            cmd = 'sed -i "/^%s=/c%s=%s" %s' % (name, name, value, self.env_path)
            output = subprocess.getoutput(cmd)
            new_envs = self.read_envs()
            value = new_envs.get(name)
            if value is not None and output == '':
                print("修改配置%s成功, 修改后的值为: '%s'" % (name, value))
                # 如果是修改的进程数配置,则设置进程数
                if name.startswith("circus_") and name.endswith("_num"):
                    server = name.replace("circus_", "").replace("_num", "")
                    cmd = 'circusctl set %s numprocesses %s' % (server, value)
                    set_ret = subprocess.getoutput(cmd)
                    if "error" not in set_ret:
                        print('设置服务%s的进程数为%s成功' % (server, value))
                    else:
                        print('设置服务%s的进程数为%s失败: %s' % (server, value, set_ret))
                ret = True
            else:
                print("修改配置%s失败: %s" % (name, output))
        return ret


if __name__ == '__main__':
    from argparse import ArgumentParser
    from importlib import import_module

    import_module("__init__")
    from common.conts import ENV_PATH

    desc = "envs manager"
    parser = ArgumentParser(description=desc)
    parser.add_argument("-ls", "--list_sections", help="show sections", action='store_true')
    parser.add_argument("-l", "--list", help="show envs", action='store_true')
    parser.add_argument("-sf", "-fs", "--fuzzy_search", help="模糊查询env的值, 将查询以指定关键词开头的env")
    parser.add_argument("-f", "--fuzzy", help="是否是模糊查询,只能配合-s/--search使用", action='store_true')
    parser.add_argument("-s", "--search", type=str, help="查询env的值")
    parser.add_argument("-c", "--clear", type=str, help="删除指定板块下的所有env")
    parser.add_argument("-u", "--update", type=str, help="更新env的值,接收两个参数name、value", nargs=2)
    parser.add_argument("-d", "--delete", type=str, help="删除一个env")
    parser.add_argument("-a", "--add", type=str,
                        help="追加一个env,接收三个参数section、name、value,将追加一个section_name=value的env", nargs=3)
    parser.add_argument("-p", "--path", type=str, default=ENV_PATH, help="env文件的路径")
    args = parser.parse_args()
    env_path = args.path
    env_manager = EnvManage(env_path)
    list_envs = args.list
    list_sections = args.list_sections
    fuzzy_keyword = args.fuzzy_search
    keyword = args.search
    update = args.update
    add = args.add
    delete = args.delete
    clear = args.clear

    if list_envs is True:
        env_manager.show_envs()
    elif list_sections:
        env_manager.show_sections()
    elif fuzzy_keyword or keyword:
        keyword = fuzzy_keyword or keyword
        fuzzy = fuzzy_keyword and True or args.fuzzy
        if fuzzy:
            env_manager.search_envs(keyword)
        else:
            env_manager.search_env(keyword)
    elif update:
        env_manager.update_env(*update)
    elif add:
        env_manager.add_env(*add)
    elif delete:
        env_manager.del_env(delete)
    elif clear:
        env_manager.del_section(clear)
    else:
        print("invalid cmd, please read the help doc")
        parser.print_help()
