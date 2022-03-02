/*
 * @Author: xiangcai
 * @Date: 2022-02-28 10:00:08
 * @LastEditors: xiangcai
 * @LastEditTime: 2022-03-02 16:30:33
 * @Description: env manager
 * 	macos需安装配置gnu-sed兼容sed命令
 */

package main

import (
	"bytes"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

	"github.com/sgs921107/gcommon"
)

var (
	circusPrefix = "circus_"
	circusSuffix = "_num"
)

func printf(format string, a ...interface{}) {
	println(fmt.Sprintf(format, a...))
}

// 执行shell
func execShell(command string) ([]byte, error) {
	return exec.Command("/bin/bash", "-c", command).Output()
}

// 复制文件
func copyFile(srcFilePath, dstFilePath string) (int64, error) {
	// 打开源文件
	srcFile, err := os.Open(srcFilePath)
	if err != nil {
		return 0, err
	}
	defer srcFile.Close()
	dstFile, err := os.OpenFile(dstFilePath, os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		return 0, err
	}
	defer dstFile.Close()
	srcMD5, err := fileMD5(srcFile)
	if err != nil {
		return 0, err
	}
	dstMD5, err := fileMD5(dstFile)
	if err != nil {
		return 0, err
	}
	// 如果文件内容一样则不执行复制
	if srcMD5 == dstMD5 {
		return 0, nil
	}
	// 游标移动至原点
	if _, err := srcFile.Seek(0, 0); err != nil {
		return 0, err
	}
	if _, err := dstFile.Seek(0, 0); err != nil {
		return 0, err
	}
	// 复制文件内容
	if written, err := io.Copy(dstFile, srcFile); err != nil {
		return 0, err
	} else {
		// 截断
		return written, dstFile.Truncate(written)
	}
}

// 文件MD5
func fileMD5(fp *os.File) (string, error) {
	cipherBytes := [md5.Size]byte{}
	for {
		buf := make([]byte, 1024)
		n, err := fp.Read(buf)
		if n > 0 {
			cipherBytes = md5.Sum(append(cipherBytes[:md5.Size], buf[:n]...))
		}
		if err == nil {
			continue
		} else if err == io.EOF {
			break
		} else {
			return "", err
		}
	}
	return hex.EncodeToString(cipherBytes[:md5.Size]), nil
}

type EnvManager struct {
	// env配置文件的路径
	envPath string
	// 对临时文件进行操作成功后回写至env path
	tmpPath string
	// 空行
	blankLineRegexp  *regexp.Regexp
	annotationRegexp *regexp.Regexp
}

// 加载env
func (m EnvManager) envs() map[string]string {
	envs, err := gcommon.ReadFileEnv(m.tmpPath)
	if err != nil {
		panic(fmt.Sprintf("Load Envs Error: %s", err.Error()))
	}
	return envs
}

// 以json格式输出
func (m EnvManager) jsonPrint(data interface{}) error {
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	var output bytes.Buffer
	if err := json.Indent(&output, b, " ", "\t"); err != nil {
		return err
	}
	fmt.Println(output.String())
	return nil
}

func (m EnvManager) showSections() {
	sectionsMap := make(map[string]int)
	for key := range m.envs() {
		section := strings.Split(key, "_")[0]
		sectionsMap[section]++
	}
	sections := make([]string, 0)
	for section := range sectionsMap {
		sections = append(sections, section)
	}
	if err := m.jsonPrint(sections); err != nil {
		printf("Show Sections Error: %s", err.Error())
	}
}

// 展示所有的env
func (m EnvManager) showEnvs() {
	if err := m.jsonPrint(m.envs()); err != nil {
		printf("Show Envs Error: %s", err.Error())
	}
}

// 查询包含指定内容的env
func (m EnvManager) sectionEnvs(section string) map[string]string {
	envs := make(map[string]string)
	for key, val := range m.envs() {
		if strings.HasPrefix(key, section) {
			envs[key] = val
		}
	}
	m.jsonPrint(envs)
	return envs
}

// 获取env的值
func (m EnvManager) get(name string) (string, bool) {
	val, ok := m.envs()[name]
	if ok {
		printf("env %s value: '%s'", name, val)
	} else {
		printf("env %s not found", name)
	}
	return val, ok
}

// 更新env
func (m EnvManager) update(name, value string) bool {
	if oriVal, ok := m.get(name); !ok {
		printf("update env %s failed: env not found", name)
		return false
	} else if oriVal == value {
		printf("env %s not need update, the value %s same as ori value %s", name, value, oriVal)
		return false
	}
	cmd := fmt.Sprintf("sed -i '/^%s=/c%s=%s' %s", name, name, value, m.tmpPath)
	if output, err := execShell(cmd); err != nil {
		printf("update env %s error: %s", name, err.Error())
		return false
	} else {
		printf("begin update env %s", name)
		if curVal, _ := m.get(name); curVal != value {
			printf("update env %s failed: %s", name, string(output))
			return false
		} else {
			if _, err := copyFile(m.tmpPath, m.envPath); err != nil {
				printf("update env %s failed, overwrite failed: %s", name, err.Error())
				return false
			}
			printf("update env %s succeed, cur value: '%s'", name, curVal)
			// 如果是circus管理的watcher进程数配置, 则设置进程数
			if strings.HasPrefix(name, circusPrefix) && strings.HasSuffix(name, circusSuffix) {
				watcher := strings.TrimSuffix(strings.TrimPrefix(name, circusPrefix), circusSuffix)
				circusCmd := fmt.Sprintf("circusctl set %s numprocesses %s", watcher, curVal)
				if output, err := execShell(circusCmd); err != nil {
					printf("set numprocesses of circus watcher %s to %s error: %s", watcher, curVal, err.Error())
				} else if strings.Contains(string(output), "error") {
					printf("set numprocesses of circus watcher %s to %s failed: %s", watcher, curVal, string(output))
				} else {
					printf("set numprocesses of circus watcher %s to %s succeed", watcher, curVal)
				}
			}
			return true
		}
	}
}

// 添加env
func (m EnvManager) addEnv(section, name, value string) bool {
	if section == "" || name == "" {
		printf("add env failed, section[%s] and name[%s] must not be empty string", section, name)
		return false
	}
	name = section + "_" + name
	if _, ok := m.get(name); ok {
		printf("env %s already exist, will be updated", name)
		return m.update(name, value)
	}
	// 尝试新增板块
	m.addSection(section)
	printf("begin add env %s", name)
	// 新增env
	addEnvCmd := fmt.Sprintf(`sed -i '/^# \[%s\]/a%s=%s' %s`, section, name, value, m.tmpPath)
	if output, err := execShell(addEnvCmd); err != nil {
		printf("add env %s error: %s", name, err.Error())
		return false
	} else {
		if curVal, _ := m.get(name); curVal != value {
			printf("add env %s failed: %s", name, string(output))
			return false
		} else {
			if _, err := copyFile(m.tmpPath, m.envPath); err != nil {
				printf("add env %s failed, overwrite failed: %s", name, err.Error())
				return false
			}
			printf("add env %s succeed, value: '%s'", name, curVal)
			return true
		}
	}
}

// 删除env
func (m EnvManager) delEnv(name string) bool {
	if _, ok := m.get(name); !ok {
		printf("del env %s failed: env not found", name)
		return false
	}
	lineCmd := fmt.Sprintf("sed -n '/^%s=/=' %s", name, m.tmpPath)
	linesOutput, err := execShell(lineCmd)
	if err != nil {
		printf("del env %s error: %s", name, err.Error())
		return false
	}
	lines := regexp.MustCompile(`\d+`).FindAll(linesOutput, -1)
	for index := len(lines) - 1; index >= 0; index-- {
		lineNo, err := strconv.Atoi(strings.TrimSpace(string(lines[index])))
		if err != nil {
			printf("del env %s failed: get env lineNo error: %s", name, err.Error())
			return false
		}
		preLine := lineNo - 1
		// 查看上一行的内容
		preLineCmd := fmt.Sprintf("sed -n '%dp' %s", preLine, m.tmpPath)
		// 如果上一行内容是注释行 则删除
		if output, _ := execShell(preLineCmd); m.annotationRegexp.Match(output) {
			delPreLineCmd := fmt.Sprintf("sed -i '%dd' %s", preLine, m.tmpPath)
			execShell(delPreLineCmd)
		}
	}
	// 删除配置行
	delEnvCmd := fmt.Sprintf("sed -i '/^%s=/d' %s", name, m.tmpPath)
	if _, err := execShell(delEnvCmd); err != nil {
		printf("Exec Del Env Cmd Error: %s", err.Error())
		return false
	}
	// 校验是否删除成功
	if curVal, ok := m.get(name); ok {
		printf("del env %s failed, value: '%s'", name, curVal)
		return false
	}
	if _, err := copyFile(m.tmpPath, m.envPath); err != nil {
		printf("del env %s failed, overwrite failed: %s", name, err.Error())
		return false
	}
	printf("del env %s succeed", name)
	return true
}

// 查询板块是否存在
func (m EnvManager) sectionLines(section string) ([]string, error) {
	cmd := fmt.Sprintf(`sed -n '/^# \[%s\]/=' %s`, section, m.tmpPath)
	if lines, err := execShell(cmd); err != nil {
		printf("Exec CMD %s Error: %s", cmd, err.Error())
		return nil, err
	} else {
		linesNo := regexp.MustCompile(`\d+`).FindAllString(string(lines), -1)
		if len(linesNo) == 0 {
			printf("section %s not found", section)
			return nil, nil
		} else {
			printf("section %s line: %s", section, strings.Join(linesNo, ", "))
			return linesNo, nil
		}
	}
}

// 添加板块
func (m EnvManager) addSection(section string) bool {
	if lines, err := m.sectionLines(section); err != nil {
		printf("Get LineNo Of The Section %s Error: %s", section, err.Error())
		return false
	} else if len(lines) > 0 {
		return false
	}
	printf("start add section %s", section)
	endLineCmd := fmt.Sprintf("tail -1 %s", m.tmpPath)
	if endLine, err := execShell(endLineCmd); err != nil {
		printf("Add Section %s Error: get end line content error: %s", section, err.Error())
		return false
		// 如果最后一行不是空行, 添加空行
	} else if !m.blankLineRegexp.Match(endLine) {
		execShell(fmt.Sprintf(`echo "" >> %s`, m.tmpPath))
	}
	// 添加section行
	execShell(fmt.Sprintf(`echo "# [%s]" >> %s`, section, m.tmpPath))
	if lines, _ := m.sectionLines(section); len(lines) > 0 {
		printf("add section %s succeed", section)
		return true
	} else {
		printf("add section %s failed", section)
		return false
	}
}

// 删除板块
func (m EnvManager) delSection(section string) bool {
	if lines, _ := m.sectionLines(section); len(lines) == 0 {
		printf("del section %s failed: get lineno failed", section)
		return false
		// 删除上面的空行
	} else {
		for index := len(lines) - 1; index >= 0; index-- {
			lineNo, err := strconv.Atoi(strings.TrimSpace(string(lines[index])))
			if err != nil {
				printf("del section %s failed: get section lineNo error: %s", section, err.Error())
				return false
			}
			// 如果是在第一行则跳过
			if lineNo == 1 {
				continue
			}
			preLine := lineNo - 1
			// 查看上一行的内容
			preLineCmd := fmt.Sprintf("sed -n '%dp' %s", preLine, m.tmpPath)
			// 如果上一行内容是空行 则删除
			if output, _ := execShell(preLineCmd); m.blankLineRegexp.Match(output) {
				delPreLineCmd := fmt.Sprintf("sed -i '%dd' %s", preLine, m.tmpPath)
				execShell(delPreLineCmd)
			}
		}
		// 删除板块
		delSectionCmd := fmt.Sprintf(`sed -i "/^# \[%s\]/d" %s`, section, m.tmpPath)
		if output, err := execShell(delSectionCmd); err != nil {
			printf("del section %s error: %s", section, err.Error())
			return false
		} else {
			// 校验是否删除成功
			if lines, _ := m.sectionLines(section); len(lines) > 0 {
				printf("del section %s failed: %s", section, string(output))
				return false
			}
			if _, err := copyFile(m.tmpPath, m.envPath); err != nil {
				printf("del section %s failed, overwrite failed: %s", section, err.Error())
				return false
			}
			printf("del section %s succeed", section)
			printf("start del envs about the section %s", section)
			for env := range m.sectionEnvs(section) {
				m.delEnv(env)
			}
			return true
		}
	}
}

// 生成EnvManager对象
func newEnvManager(envPath, tmpPath string) EnvManager {
	// 复制env到临时文件
	if _, err := copyFile(envPath, tmpPath); err != nil {
		panic(fmt.Sprintf("copy env path to tmpPath error: %s", err.Error()))
	}
	manager := EnvManager{
		envPath: envPath,
		tmpPath: tmpPath,
		// 空白行
		blankLineRegexp: regexp.MustCompile(`^\s*$`),
		// 注释行
		annotationRegexp: regexp.MustCompile(`^\s*#[^\[]*$`),
	}
	return manager
}

func main() {
	var defaultEnvPath, tmpPath = ".env", "/tmp/temp_env"
	var envs, sections, update, add bool
	var env, section, clear, delete, path string
	flag.BoolVar(&envs, "l", false, "-l: list envs")
	flag.BoolVar(&sections, "ls", false, "-ls: list sections")
	flag.StringVar(&env, "s", "", "-s env: search env")
	flag.StringVar(&section, "ss", "", "-ss section: search section envs")
	flag.BoolVar(&update, "u", false, "-u env value: update env")
	flag.BoolVar(&add, "a", false, "-a section name value: add env")
	flag.StringVar(&delete, "d", "", "-d env: del env")
	flag.StringVar(&clear, "c", "", "-c section: clear section envs")
	flag.StringVar(&path, "path", defaultEnvPath, "-path path: env path")
	flag.Parse()
	manager := newEnvManager(path, tmpPath)
	args := flag.Args()
	nArg := flag.NArg()
	if envs {
		manager.showEnvs()
	} else if sections {
		manager.showSections()
	} else if env != "" {
		manager.get(env)
	} else if section != "" {
		manager.sectionEnvs(section)
	} else if add && nArg == 3 {
		manager.addEnv(args[0], args[1], args[2])
	} else if update && nArg == 2 {
		manager.update(args[0], args[1])
	} else if delete != "" {
		manager.delEnv(delete)
	} else if clear != "" {
		manager.delSection(clear)
	} else {
		flag.Usage()
	}
}
